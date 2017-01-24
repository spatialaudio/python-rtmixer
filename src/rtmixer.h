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

typedef unsigned long frame_t;

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
  bool allow_belated;
  PaTime requested_time;
  PaTime actual_time;
  struct action* next;
  union {
    float* const buffer;
    PaUtilRingBuffer* const ringbuffer;
  };
  const frame_t total_frames;
  frame_t done_frames;
  // TODO: something to store the result of the action?
  const frame_t channels;  // Size of the following array
  const frame_t mapping[];  // "flexible array member"
};

struct state
{
  const frame_t input_channels;
  const frame_t output_channels;
  double samplerate;
  PaUtilRingBuffer* const action_q;  // Queue for incoming commands
  PaUtilRingBuffer* const result_q;  // Queue for results and command disposal
  struct action* actions;  // Singly linked list of actions
};

int callback(const void* input, void* output, frame_t frames
  , const PaStreamCallbackTimeInfo* time, PaStreamCallbackFlags status
  , void* userdata);
