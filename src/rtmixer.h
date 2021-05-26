/* From portaudio.h: */
typedef double PaTime;
typedef struct PaStreamCallbackTimeInfo PaStreamCallbackTimeInfo;
typedef unsigned long PaStreamCallbackFlags;
/* End of declarations from portaudio.h */

typedef unsigned long frame_t;
struct PaUtilRingBuffer;

enum actiontype
{
  PLAY_BUFFER,
  PLAY_RINGBUFFER,
  RECORD_BUFFER,
  RECORD_RINGBUFFER,
  CANCEL,
  FETCH_AND_RESET_STATS,
};

struct stats
{
  frame_t blocks;
  frame_t min_blocksize;
  frame_t max_blocksize;
  frame_t input_underflows;
  frame_t input_overflows;
  frame_t output_underflows;
  frame_t output_overflows;
};

struct action
{
  const enum actiontype type;
  const PaTime requested_time;
  PaTime actual_time;  // Set != 0.0 to allow belated actions
  struct action* next;  // Used to create singly linked list of actions
  union {
    float* const buffer;
    struct PaUtilRingBuffer* const ringbuffer;
    struct action* const action;  // Used in CANCEL
  };
  frame_t total_frames;
  frame_t done_frames;
  struct stats stats;
  // TODO: ringbuffer usage: store smallest available write/read size?
  const frame_t channels;  // Size of the following array
  const frame_t mapping[];  // "flexible array member"
};

struct state
{
  const frame_t input_channels;
  const frame_t output_channels;
  double samplerate;
  struct PaUtilRingBuffer* const action_q;  // Queue for incoming commands
  struct PaUtilRingBuffer* const result_q;  // Q for results and cmd disposal
  struct action* actions;  // Singly linked list of actions
  struct stats stats;
  // TODO: result_q usage?
};

int callback(const void* input, void* output, frame_t frameCount
  , const PaStreamCallbackTimeInfo* timeInfo, PaStreamCallbackFlags statusFlags
  , void* userData);
