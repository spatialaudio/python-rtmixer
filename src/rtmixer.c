/* See ../rtmixer_build.py */

#include <assert.h>  // for assert()
#include <math.h>  // for llround()
#include <stdbool.h>  // for bool, true, false

#include <portaudio.h>
#include <pa_ringbuffer.h>

#include "rtmixer.h"

struct action** remove_action(struct action** addr, struct state* state)
{
  struct action* action = *addr;
  *addr = action->next;  // Current action is removed from list
  action->next = NULL;
  ring_buffer_size_t written = PaUtil_WriteRingBuffer(state->result_q
    , &action, 1);
  if (written != 1)
  {
    // TODO: do something? Stop callback? Log error (in "state")?
    printf("result queue is full\n");
  }
  return addr;  // The same address, which now holds a new pointer
}

int callback(const void* input, void* output, frame_t frameCount
  , const PaStreamCallbackTimeInfo* timeInfo, PaStreamCallbackFlags statusFlags
  , void* userData)
{
  struct state* state = userData;

  memset(output, 0, sizeof(float) * state->output_channels * frameCount);

  if (statusFlags & paInputUnderflow)  { printf("Input underflow!\n"); }
  if (statusFlags & paInputOverflow)   { printf("Input overflow!\n"); }
  if (statusFlags & paOutputUnderflow) { printf("Output underflow!\n"); }
  if (statusFlags & paOutputOverflow)  { printf("Output overflow!\n"); }

  // TODO: store information about overflows/underflows

  // TODO: check if main thread is still running?

  for (struct action* action = NULL
      ; PaUtil_ReadRingBuffer(state->action_q, &action, 1)
      ;)
  {
    // TODO: check action type, remove things if necessary

    // Note: actions are added at the beginning of the list, because its easier:
    action->next = state->actions;
    state->actions = action;
  }

  // Using pointer-to-pointer to be able to remove list elements
  for (struct action ** actionaddr = &(state->actions), ** nextaddr = NULL
      ; *actionaddr
      ; actionaddr = nextaddr)
  {
    struct action* const action = *actionaddr;
    nextaddr = &(action->next);

    const bool playing = action->type == PLAY_BUFFER
                      || action->type == PLAY_RINGBUFFER;
    const bool recording = action->type == RECORD_BUFFER
                        || action->type == RECORD_RINGBUFFER;
    const bool using_buffer = action->type == PLAY_BUFFER
                           || action->type == RECORD_BUFFER;
    const bool using_ringbuffer = action->type == PLAY_RINGBUFFER
                               || action->type == RECORD_RINGBUFFER;
    PaTime io_time = 0;
    if (playing)
    {
      io_time = timeInfo->outputBufferDacTime;
    }
    if (recording)
    {
      io_time = timeInfo->inputBufferAdcTime;
    }

    frame_t offset = 0;

    if (action->done_frames == 0)
    {
      PaTime diff = action->requested_time - io_time;
      if (diff >= 0.0)
      {
        offset = (frame_t)llround(diff * state->samplerate);
        if (offset >= frameCount)
        {
          // We are too early!

          // Due to inaccuracies in timeInfo, "diff" might have a small negative
          // value in a future block.  We don't count this as "belated" though:
          action->allow_belated = true;
          continue;
        }
        // Re-calculate "diff" to propagate rounding errors
        action->actual_time = io_time + (double)offset / state->samplerate;
      }
      else
      {
        // We are too late!
        if (!action->allow_belated)
        {
          action->actual_time = 0.0;  // a.k.a. "false"
          nextaddr = remove_action(actionaddr, state);
          continue;
        }
        action->actual_time = io_time;
      }
    }

    float* target = NULL;
    float* source = NULL;

    if (playing)
    {
      target = (float*)output + offset * state->output_channels;
    }
    else if (recording)
    {
      source = (float*)input + offset * state->input_channels;
    }

    frame_t frames = 0;

    if (using_buffer)
    {
      frames = action->total_frames - action->done_frames;
      if (frameCount < frames)
      {
        frames = frameCount;
      }
      if (frames + offset > frameCount)
      {
        assert(frameCount > offset);
        frames = frameCount - offset;
      }
      if (playing)
      {
        float* source = action->buffer + action->done_frames * action->channels;
        action->done_frames += frames;
        while (frames--)
        {
          for (frame_t c = 0; c < action->channels; c++)
          {
            target[action->mapping[c] - 1] += *source++;
          }
          target += state->output_channels;
        }
      }
      else if (recording)
      {
        float* target = action->buffer + action->done_frames * action->channels;
        action->done_frames += frames;
        while (frames--)
        {
          for (frame_t c = 0; c < action->channels; c++)
          {
            *target++ = source[action->mapping[c] - 1];
          }
          source += state->input_channels;
        }
      }
      if (action->done_frames == action->total_frames)
      {
        nextaddr = remove_action(actionaddr, state);
      }
    }
    else if (using_ringbuffer)
    {
      // TODO: continue to ignore action->total_frames?

      float* block1 = NULL;
      float* block2 = NULL;
      ring_buffer_size_t size1 = 0;
      ring_buffer_size_t size2 = 0;
      ring_buffer_size_t totalsize = 0;

      if (playing)
      {
        totalsize = PaUtil_GetRingBufferReadRegions(action->ringbuffer
          , (ring_buffer_size_t)(frameCount - offset)
          , (void**)&block1, &size1, (void**)&block2, &size2);

        while (size1--)
        {
          for (frame_t c = 0; c < action->channels; c++)
          {
            target[action->mapping[c] - 1] += *block1++;
          }
          target += state->output_channels;
        }
        while (size2--)
        {
          for (frame_t c = 0; c < action->channels; c++)
          {
            target[action->mapping[c] - 1] += *block2++;
          }
          target += state->output_channels;
        }
        action->done_frames += (frame_t)totalsize;
        PaUtil_AdvanceRingBufferReadIndex(action->ringbuffer, totalsize);
      }
      else if (recording)
      {
        totalsize = PaUtil_GetRingBufferWriteRegions(action->ringbuffer
          , (ring_buffer_size_t)(frameCount - offset)
          , (void**)&block1, &size1, (void**)&block2, &size2);

        while (size1--)
        {
          for (frame_t c = 0; c < action->channels; c++)
          {
             *block1++ = source[action->mapping[c] - 1];
          }
          source += state->input_channels;
        }
        while (size2--)
        {
          for (frame_t c = 0; c < action->channels; c++)
          {
            *block2++ = source[action->mapping[c] - 1];
          }
          source += state->input_channels;
        }
        action->done_frames += (frame_t)totalsize;
        PaUtil_AdvanceRingBufferWriteIndex(action->ringbuffer, totalsize);
      }

      if (totalsize < frameCount - offset)
      {
        // Ring buffer is empty or full

        // TODO: store some information in action?

        nextaddr = remove_action(actionaddr, state);
      }
    }
  }
  return paContinue;
}
