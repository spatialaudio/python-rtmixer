/* See ../rtmixer_build.py */

#include <math.h>  // for llround()
#include <stdbool.h>  // for bool, true, false

#include <portaudio.h>
#include <pa_ringbuffer.h>

#include "rtmixer.h"

#ifdef NDEBUG
#define CALLBACK_ASSERT(expr) ((void)(0))
#else
#define CALLBACK_ASSERT(expr) \
  do { if (!(expr)) { \
    printf("Failed assertion in audio callback: \"" #expr "\" (" __FILE__ \
        ":%i)\n", __LINE__); \
    return paAbort; \
  }} while (false)
#endif

void remove_action(struct action** addr, struct state* state)
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
}

int callback(const void* input, void* output, frame_t frameCount
  , const PaStreamCallbackTimeInfo* timeInfo, PaStreamCallbackFlags statusFlags
  , void* userData)
{
  struct state* state = userData;
  CALLBACK_ASSERT(state);

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
    // Actions are added at the beginning of the list, because CANCEL actions
    // must come before the action they are cancelling.  Also, it's easier.
    struct action* i = action;
    while (i->next)
    {
      i = i->next;
    }
    i->next = state->actions;
    state->actions = action;
  }

  struct action** actionaddr = &(state->actions);
  while (*actionaddr)
  {
    struct action* const action = *actionaddr;

    enum actiontype type = action->type;
    if (type == CANCEL)
    {
      CALLBACK_ASSERT(action->action);
      type = action->action->type;
    }
    const bool playing = type == PLAY_BUFFER || type == PLAY_RINGBUFFER;

    PaTime io_time = playing ? timeInfo->outputBufferDacTime
                             : timeInfo->inputBufferAdcTime;
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
          actionaddr = &(action->next);
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
          remove_action(actionaddr, state);
          continue;
        }
        action->actual_time = io_time;
      }
    }

    if (action->type == CANCEL)
    {
      for (struct action** i = &(action->next); *i; i = &((*i)->next))
      {
        if (*i == action->action)
        {
          struct action* delinquent = *i;

          if (delinquent->done_frames + offset > delinquent->total_frames)
          {
            // TODO: stops on its own ... set some error state?
          }
          else
          {
            delinquent->total_frames = delinquent->done_frames + offset;
          }
          // TODO: save some informations to action->...?
          break;
        }
      }
      // TODO: what if the action to cancel wasn't found? set actual_time = 0.0?

      remove_action(actionaddr, state);  // Remove the CANCEL action itself
      continue;
    }

    frame_t frames = action->total_frames - action->done_frames;

    if (frameCount < frames)
    {
      frames = frameCount;
    }
    if (frames + offset > frameCount)
    {
      CALLBACK_ASSERT(frameCount > offset);
      frames = frameCount - offset;
    }

    float* device_data
      = playing ? (float*)output + offset * state->output_channels
                : (float*) input + offset * state->input_channels;

    if (action->type == PLAY_BUFFER || action->type == RECORD_BUFFER)
    {
      float* buffer = action->buffer + action->done_frames * action->channels;
      action->done_frames += frames;
      if (action->type == PLAY_BUFFER)
      {
        while (frames--)
        {
          for (frame_t c = 0; c < action->channels; c++)
          {
            device_data[action->mapping[c] - 1] += *buffer++;
          }
          device_data += state->output_channels;
        }
      }
      else
      {
        CALLBACK_ASSERT(action->type == RECORD_BUFFER);

        while (frames--)
        {
          for (frame_t c = 0; c < action->channels; c++)
          {
            *buffer++ = device_data[action->mapping[c] - 1];
          }
          device_data += state->input_channels;
        }
      }
    }
    else
    {
      CALLBACK_ASSERT(action->type ==   PLAY_RINGBUFFER
                   || action->type == RECORD_RINGBUFFER);

      float* block1 = NULL;
      float* block2 = NULL;
      ring_buffer_size_t size1 = 0;
      ring_buffer_size_t size2 = 0;
      ring_buffer_size_t totalsize = 0;

      if (action->type == PLAY_RINGBUFFER)
      {
        totalsize = PaUtil_GetRingBufferReadRegions(action->ringbuffer
          , (ring_buffer_size_t)frames
          , (void**)&block1, &size1, (void**)&block2, &size2);

        while (size1--)
        {
          for (frame_t c = 0; c < action->channels; c++)
          {
            device_data[action->mapping[c] - 1] += *block1++;
          }
          device_data += state->output_channels;
        }
        while (size2--)
        {
          for (frame_t c = 0; c < action->channels; c++)
          {
            device_data[action->mapping[c] - 1] += *block2++;
          }
          device_data += state->output_channels;
        }
        action->done_frames += (frame_t)totalsize;
        PaUtil_AdvanceRingBufferReadIndex(action->ringbuffer, totalsize);
      }
      else
      {
        CALLBACK_ASSERT(action->type == RECORD_RINGBUFFER);

        totalsize = PaUtil_GetRingBufferWriteRegions(action->ringbuffer
          , (ring_buffer_size_t)frames
          , (void**)&block1, &size1, (void**)&block2, &size2);

        while (size1--)
        {
          for (frame_t c = 0; c < action->channels; c++)
          {
             *block1++ = device_data[action->mapping[c] - 1];
          }
          device_data += state->input_channels;
        }
        while (size2--)
        {
          for (frame_t c = 0; c < action->channels; c++)
          {
            *block2++ = device_data[action->mapping[c] - 1];
          }
          device_data += state->input_channels;
        }
        action->done_frames += (frame_t)totalsize;
        PaUtil_AdvanceRingBufferWriteIndex(action->ringbuffer, totalsize);
      }

      if (totalsize < frames)
      {
        // Ring buffer is empty or full

        // TODO: store some information in action?

        remove_action(actionaddr, state);
        continue;
      }
    }

    if (action->done_frames == action->total_frames)
    {
      remove_action(actionaddr, state);
      continue;
    }
    actionaddr = &(action->next);
  }
  return paContinue;
}
