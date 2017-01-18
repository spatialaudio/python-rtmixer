/* See rtmixer_build.py */

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
      // TODO: floor?
      offset = (frame_t)(diff * state->samplerate);
      // Re-calculate "diff" to get rounding errors
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
        float* target = output;

        frames -= offset;
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
        float* target = output;
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
        // TODO
        break;
      }
      case RECORD_RINGBUFFER:
      {
        // TODO
        break;
      }
      default:
        ;
        // TODO: error!
    }
next_action:
    action = action->next;
  }

  // Note: input data is ignored for now

  return paContinue;
}
