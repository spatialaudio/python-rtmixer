/* From portaudio.h: */
typedef double PaTime;
typedef struct PaStreamCallbackTimeInfo PaStreamCallbackTimeInfo;
typedef unsigned long PaStreamCallbackFlags;
/* End of declarations from portaudio.h */

typedef unsigned long frame_t;

enum actiontype
{
  PLAY_BUFFER,
  PLAY_RINGBUFFER,
  RECORD_BUFFER,
  RECORD_RINGBUFFER,
  CANCEL,
  // TODO: action to query xrun stats etc.?
};

struct stats
{
  frame_t blocks;
  frame_t input_underflows;
  frame_t input_overflows;
  frame_t output_underflows;
  frame_t output_overflows;
};

struct action
{
  const enum actiontype type;
  bool allow_belated;
  PaTime requested_time;
  PaTime actual_time;
  struct action* next;
  union {
    float* const buffer;
    PaUtilRingBuffer* const ringbuffer;
    struct action* action;  // Used in CANCEL
  };
  frame_t total_frames;
  frame_t done_frames;
  // TODO: something to store the result of the action?
  struct stats stats;
  // TODO: queue usage: store smallest available write/read size?
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
  struct stats stats;
};

int callback(const void* input, void* output, frame_t frameCount
  , const PaStreamCallbackTimeInfo* timeInfo, PaStreamCallbackFlags statusFlags
  , void* userData);
