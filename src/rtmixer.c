/* See rtmixer_build.py */

#include <assert.h>  // for assert()
#include <math.h>  // for llround()
#include <portaudio.h>
#include <pa_ringbuffer.h>
#include "rtmixer.h"

frame_t get_offset(PaTime time, struct action* action, struct state* state)
{
  frame_t offset = 0;
  if (action->done_frames == 0)
  {
    PaTime diff = action->requested_time - time;
    if (diff > 0)
    {
      offset = (frame_t)llround(diff * state->samplerate);
      // Re-calculate "diff" to propagate rounding errors
      action->actual_time = time + (double)offset / state->samplerate;
    }
    else
    {
      // We are too late!
      action->actual_time = time;
    }
  }
  return offset;
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

  struct action* action = NULL;
  while (PaUtil_ReadRingBuffer(state->action_q, &action, 1))
  {
    // TODO: check action type, remove things if necessary

    // Note: actions are added at the beginning of the list, because its easier:
    action->next = state->actions;
    state->actions = action;
  }

  action = state->actions;
  while (action)
  {
    switch (action->actiontype)
    {
      case PLAY_BUFFER:
      {
        frame_t offset = get_offset(timeInfo->outputBufferDacTime,
                                    action, state);
        if (offset >= frameCount)
        {
          // We are too early!
          goto next_action;
        }
        frame_t frames = action->total_frames - action->done_frames;
        if (frameCount < frames)
        {
          frames = frameCount;
        }
        float* target = (float*)output;

        if (frames + offset > frameCount)
        {
          assert(frameCount > offset);
          frames = frameCount - offset;
        }
        target += offset * state->output_channels;

        float* source = action->buffer;
        source += action->done_frames * action->channels;
        action->done_frames += frames;
        while (frames--)
        {
          for (frame_t c = 0; c < action->channels; c++)
          {
            target[action->mapping[c] - 1] += *source++;
          }
          target += state->output_channels;
        }
        if (action->done_frames == action->total_frames)
        {
          // TODO: stop playback, discard action struct
        }
        break;
      }
      case PLAY_RINGBUFFER:
      {
        // TODO: continue to ignore action->total_frames?

        frame_t offset = get_offset(timeInfo->outputBufferDacTime,
                                    action, state);
        if (offset >= frameCount)
        {
          // We are too early!
          goto next_action;
        }
        float* target = (float*)output;
        target += offset * state->output_channels;
        float* block1 = NULL;
        float* block2 = NULL;
        ring_buffer_size_t size1 = 0;
        ring_buffer_size_t size2 = 0;

        ring_buffer_size_t read_elements = PaUtil_GetRingBufferReadRegions(
            action->ringbuffer, (ring_buffer_size_t)(frameCount - offset),
            (void**)&block1, &size1, (void**)&block2, &size2);

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
        action->done_frames += (frame_t)read_elements;
        PaUtil_AdvanceRingBufferReadIndex(action->ringbuffer, read_elements);

        // TODO: if ringbuffer is empty, stop playback, discard action struct
        break;
      }
      case RECORD_BUFFER:
      {
        frame_t offset = get_offset(timeInfo->inputBufferAdcTime,
                                    action, state);
        if (offset >= frameCount)
        {
          // We are too early!
          goto next_action;
        }
        frame_t frames = action->total_frames - action->done_frames;
        if (frameCount < frames)
        {
          frames = frameCount;
        }
        float* source = (float*)input;

        if (frames + offset > frameCount)
        {
          assert(frameCount > offset);
          frames = frameCount - offset;
        }
        source += offset * state->input_channels;

        float* target = action->buffer;
        target += action->done_frames * action->channels;
        action->done_frames += frames;
        while (frames--)
        {
          for (frame_t c = 0; c < action->channels; c++)
          {
            *target++ = source[action->mapping[c] - 1];
          }
          source += state->input_channels;
        }
        if (action->done_frames == action->total_frames)
        {
          // TODO: stop recording, discard action struct
        }
        break;
      }
      case RECORD_RINGBUFFER:
      {
        // TODO: continue to ignore action->total_frames?

        frame_t offset = get_offset(timeInfo->inputBufferAdcTime,
                                    action, state);
        if (offset >= frameCount)
        {
          // We are too early!
          goto next_action;
        }
        float* source = (float*)input;
        source += offset * state->input_channels;
        float* block1 = NULL;
        float* block2 = NULL;
        ring_buffer_size_t size1 = 0;
        ring_buffer_size_t size2 = 0;

        ring_buffer_size_t written = PaUtil_GetRingBufferWriteRegions(
            action->ringbuffer, (ring_buffer_size_t)(frameCount - offset),
            (void**)&block1, &size1, (void**)&block2, &size2);

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
        action->done_frames += (frame_t)written;
        PaUtil_AdvanceRingBufferWriteIndex(action->ringbuffer, written);

        // TODO: if ringbuffer is empty, stop playback, discard action struct
        break;
      }
      default:
        ;
        // TODO: error!
    }
next_action:
    action = action->next;
  }

  return paContinue;
}
