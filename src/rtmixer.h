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
  struct action* next;
  union {
    float* const buffer;
    PaUtilRingBuffer* const ringbuffer;
  };
  const unsigned long total_frames;
  unsigned long done_frames;
  // TODO: channel mapping (pointer to list of channels + length)
  // TODO: something to store the result of the action?
};

struct state
{
  const int input_channels;
  const int output_channels;
  PaUtilRingBuffer* const action_q;  // Queue for incoming commands
  PaUtilRingBuffer* const result_q;  // Queue for results and command disposal
  struct action* actions;  // Singly linked list of actions
};

int callback(const void* input, void* output, unsigned long frames
  , const PaStreamCallbackTimeInfo* time, PaStreamCallbackFlags status
  , void* userdata);
