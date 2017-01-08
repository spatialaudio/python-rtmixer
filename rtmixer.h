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
  enum actiontype actiontype;
  PaUtilRingBuffer* ringbuffer;
  float* buffer;
  unsigned long total_frames;
  unsigned long done_frames;
  // TODO: channel mapping (pointer to list of channels + length)
  // TODO: something to store the result of the action?
  struct action* next;
};

struct state
{
  int input_channels;
  int output_channels;
  PaUtilRingBuffer* action_q;  // Queue for incoming commands
  PaUtilRingBuffer* result_q;  // Queue for results and command disposal
  struct action* actions;  // Singly linked list of actions
};

int callback(const void* input, void* output, unsigned long frames
  , const PaStreamCallbackTimeInfo* time, PaStreamCallbackFlags status
  , void* userdata);
