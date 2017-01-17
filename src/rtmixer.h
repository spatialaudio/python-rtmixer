// actions:
//
// * read from queue
// * read from array
// * write to queue
// * write to array
// * stop action (with and/or without time?)
// * query xrun stats etc.
// timestamp! start, duration (number of samples? unlimited?)
// return values: actual start, actual duration (number of samples?)
//   queue usage: store smallest available write/read size
//   xruns during the runtime of the current action
//
// if queue is empty/full, stop playback/recording

enum actiontype
{
  PLAY_BUFFER,
  PLAY_RINGBUFFER,
  RECORD_BUFFER,
  RECORD_RINGBUFFER,
};

struct action
{
  const enum actiontype actiontype;
  PaTime requested_time;
  PaTime actual_time;
  struct action* next;
  union {
    float* const buffer;
    PaUtilRingBuffer* const ringbuffer;
  };
  const unsigned long total_frames;
  unsigned long done_frames;
  // TODO: something to store the result of the action?
  const int channels;
  const int mapping[];  // "flexible array member", size given by "channels"
};

struct state
{
  const int input_channels;
  const int output_channels;
  double samplerate;
  PaUtilRingBuffer* const action_q;  // Queue for incoming commands
  PaUtilRingBuffer* const result_q;  // Queue for results and command disposal
  struct action* actions;  // Singly linked list of actions
};

int callback(const void* input, void* output, unsigned long frames
  , const PaStreamCallbackTimeInfo* time, PaStreamCallbackFlags status
  , void* userdata);
