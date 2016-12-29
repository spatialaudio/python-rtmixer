typedef struct
{
  int input_channels;
  int output_channels;
  PaUtilRingBuffer* rb_ptr;
}
state_t;

int callback(const void* input, void* output, unsigned long frames
  , const PaStreamCallbackTimeInfo* time, PaStreamCallbackFlags status
  , void* userdata);
