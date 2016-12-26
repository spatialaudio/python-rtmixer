/* See rtmixer_build.py */

#include <portaudio.h>

int callback(const void* input, void* output, unsigned long frames
  , const PaStreamCallbackTimeInfo* time, PaStreamCallbackFlags status
  , void* userdata)
{
  // TODO: check if main thread is still running?

  return paContinue;
}
