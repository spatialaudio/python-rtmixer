/* See rtmixer_build.py */

#include <portaudio.h>
#include <pa_ringbuffer.h>
#include "rtmixer.h"

int callback(const void* input, void* output, unsigned long frameCount
  , const PaStreamCallbackTimeInfo* timeInfo, PaStreamCallbackFlags statusFlags
  , void* userData)
{
  float* outdata = output;
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
    // TODO: append new actions to the end of the list?
    action->next = state->actions;
    state->actions = action;
  }

  action = state->actions;
  while (action)
  {
    // TODO: check action type

    float* block1 = NULL;
    float* block2 = NULL;
    ring_buffer_size_t size1 = 0;
    ring_buffer_size_t size2 = 0;

    ring_buffer_size_t read_elements = PaUtil_GetRingBufferReadRegions(
        action->ringbuffer, frameCount, (void**)&block1, &size1,
                                        (void**)&block2, &size2);

    PaUtil_AdvanceRingBufferReadIndex(action->ringbuffer, read_elements);

    float* target = outdata;
    while (size1--)
    {
      *target++ += *block1++;
    }
    while (size2--)
    {
      *target++ += *block2++;
    }

    // TODO: if ringbuffer is empty, stop playback

    action = action->next;
  }

  // Note: input data is ignored for now

  return paContinue;
}
