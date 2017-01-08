/* See rtmixer_build.py */

#include <portaudio.h>
#include <pa_ringbuffer.h>
#include "rtmixer.h"

int callback(const void* input, void* output, unsigned long frameCount
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
        float* target = output;
        unsigned long frames = action->total_frames - action->done_frames;
        if (frameCount < frames)
        {
          frames = frameCount;
        }

        if (action->done_frames == 0)
        {
          // TODO: get start time, increment target, decrement frames
          // TODO: store timestamp of actual start of playback
        }
        float* source =
          action->buffer + action->done_frames * state->output_channels;
        unsigned long size = frames * state->output_channels;
        while (size--)
        {
          *target++ += *source++;
        }
        action->done_frames += frames;
        if (action->done_frames == action->total_frames)
        {
          // TODO: stop playback, discard action struct
        }
        break;
      }
      case PLAY_RINGBUFFER:
      {
        // TODO: continue to ignore action->total_frames?

        // TODO: get start time
        // TODO: store timestamp of actual start of playback
        float* block1 = NULL;
        float* block2 = NULL;
        ring_buffer_size_t size1 = 0;
        ring_buffer_size_t size2 = 0;

        ring_buffer_size_t read_elements = PaUtil_GetRingBufferReadRegions(
            action->ringbuffer, (ring_buffer_size_t)frameCount,
            (void**)&block1, &size1, (void**)&block2, &size2);

        PaUtil_AdvanceRingBufferReadIndex(action->ringbuffer, read_elements);

        // Sizes are in frames, we need samples:
        size1 *= state->output_channels;
        size2 *= state->output_channels;

        float* target = output;
        while (size1--)
        {
          *target++ += *block1++;
        }
        while (size2--)
        {
          *target++ += *block2++;
        }
        action->done_frames += read_elements;
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
    action = action->next;
  }

  // Note: input data is ignored for now

  return paContinue;
}
