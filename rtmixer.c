/* See rtmixer_build.py */

#include <portaudio.h>
#include <pa_ringbuffer.h>
#include "rtmixer.h"

int callback(const void* input, void* output, unsigned long frameCount
  , const PaStreamCallbackTimeInfo* timeInfo, PaStreamCallbackFlags statusFlags
  , void* userData)
{
  // TODO: check if main thread is still running?

  state_t* state = userData;

  if (statusFlags & paInputUnderflow) { printf("Input underflow!\n"); }
  if (statusFlags & paInputOverflow)  { printf("Input overflow!\n"); }
  if (statusFlags & paOutputUnderflow) { printf("Output underflow!\n"); }
  if (statusFlags & paOutputOverflow)  { printf("Output overflow!\n"); }

  PaUtilRingBuffer* const rb = state->rb_ptr;

  if (PaUtil_GetRingBufferReadAvailable(rb))
  {
    ring_buffer_size_t elements_read = PaUtil_ReadRingBuffer(rb, output, 1);
    if (elements_read != 1)
    {
      printf("Error reading ring buffer!\n");
      return paAbort;
    }
  }
  else
  {
    memset(output, 0, sizeof(float) * state->output_channels * frameCount);
  }

  // Note: input data is ignored for now

  return paContinue;
}
