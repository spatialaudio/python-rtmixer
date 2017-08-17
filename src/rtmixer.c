/* See ../rtmixer_build.py, the ring buffer declarations are included there */

#include <math.h>  // for llround()
#include <stdio.h>  // for printf()
#include <string.h>  // for memset()
#include <portaudio.h>
#include "rtmixer.h"

#ifdef NDEBUG
#define CALLBACK_ASSERT(expr) ((void)(0))
#else
#define CALLBACK_ASSERT(expr) \
  do { if (!(expr)) { \
    printf("Failed assertion in audio callback: \"" #expr "\" (" __FILE__ \
        ":%i)\n", __LINE__); \
    return paAbort; \
  }} while (false)
#endif

void remove_action(struct action** addr, const struct state* state)
{
  struct action* action = *addr;
  *addr = action->next;  // Current action is removed from list
  action->next = NULL;
  ring_buffer_size_t written = PaUtil_WriteRingBuffer(state->result_q
    , &action, 1);
  if (written != 1)
  {
    // TODO: do something? Stop callback? Log error (in "state")?
    printf("result queue is full\n");
  }
}

void get_stats(PaStreamCallbackFlags flags, struct stats* stats)
{
  stats->blocks++;

  if (flags & paInputUnderflow)  { stats->input_underflows++; }
  if (flags & paInputOverflow)   { stats->input_overflows++; }
  if (flags & paOutputUnderflow) { stats->output_underflows++; }
  if (flags & paOutputOverflow)  { stats->output_overflows++; }
}

frame_t seconds2samples(PaTime time, double samplerate)
{
  return (frame_t) llround(time * samplerate);
}

int callback(const void* input, void* output, frame_t frameCount
  , const PaStreamCallbackTimeInfo* timeInfo, PaStreamCallbackFlags statusFlags
  , void* userData)
{
  struct state* state = userData;
  CALLBACK_ASSERT(state);

  memset(output, 0, sizeof(float) * state->output_channels * frameCount);

  get_stats(statusFlags, &(state->stats));

  for (struct action* action = NULL
      ; PaUtil_ReadRingBuffer(state->action_q, &action, 1)
      ;)
  {
    // Actions are added at the beginning of the list, because CANCEL actions
    // must come before the action they are cancelling.  Also, it's easier.
    struct action* i = action;
    while (i->next)
    {
      i = i->next;
    }
    i->next = state->actions;
    state->actions = action;
  }

  struct action** actionaddr = &(state->actions);
  while (*actionaddr)
  {
    struct action* const action = *actionaddr;

    enum actiontype type = action->type;
    if (type == CANCEL)
    {
      CALLBACK_ASSERT(action->action);
      type = action->action->type;
    }
    const bool playing = type == PLAY_BUFFER || type == PLAY_RINGBUFFER;

    PaTime io_time = playing ? timeInfo->outputBufferDacTime
                             : timeInfo->inputBufferAdcTime;
    frame_t offset = 0;

    // Check if the action is due to start in the current block

    if (action->done_frames == 0)
    {
      // This action has not yet been "active"

      PaTime diff = action->requested_time - io_time;
      if (diff >= 0.0)
      {
        offset = seconds2samples(diff, state->samplerate);
        if (offset >= frameCount)
        {
          // We are too early, let's continue in the next block!

          // Due to inaccuracies in timeInfo, "diff" might have a small negative
          // value in a future block.  We don't count this as "belated" though:
          action->allow_belated = true;
          actionaddr = &(action->next);
          continue;
        }
        // Re-calculate "diff" to propagate rounding errors
        action->actual_time = io_time + (double)offset / state->samplerate;
      }
      else
      {
        // We are too late!
        if (!action->allow_belated)
        {
          action->actual_time = 0.0;  // a.k.a. "false"
          remove_action(actionaddr, state);
          continue;
        }
        action->actual_time = io_time;
      }
    }

    // Handle CANCEL action

    if (action->type == CANCEL)
    {
      // Search the following list items, not the preceding ones!
      for (struct action** i = &(action->next); *i; i = &((*i)->next))
      {
        if (*i == action->action)
        {
          struct action* delinquent = *i;

          if (delinquent->done_frames == 0)
          {
            // delinquent is not yet playing/recording

            frame_t delinquent_offset = 0;
            PaTime diff = delinquent->requested_time - io_time;
            if (diff >= 0.0)
            {
              delinquent_offset = seconds2samples(diff, state->samplerate);
              if (delinquent_offset >= offset)
              {
                // Removal is scheduled before playback/recording begins

                // TODO: save some status information?
                remove_action(i, state);
                break;
              }
            }
            else
            {
              if (!delinquent->allow_belated)
              {
                // TODO: save some status information?
                break;  // The action will not be started, no need to cancel it
              }
            }

            if (delinquent->total_frames + delinquent_offset > offset)
            {
              CALLBACK_ASSERT(offset >= delinquent_offset);
              delinquent->total_frames = offset - delinquent_offset;
            }
            else
            {
              // TODO: stops on its own ... save some status information?
            }
          }
          else
          {
            CALLBACK_ASSERT(
                delinquent->total_frames >= delinquent->done_frames);
            if (delinquent->total_frames - delinquent->done_frames > offset)
            {
              delinquent->total_frames = delinquent->done_frames + offset;
            }
            else
            {
              // TODO: stops on its own ... save some status information?
            }
          }
          // TODO: save some informations to action->...?

          break;  // We found the action, no need to keep searching
        }
      }
      // TODO: what if the action to cancel wasn't found?

      remove_action(actionaddr, state);  // Remove the CANCEL action itself
      continue;
    }

    // Store buffer over-/underflow information

    get_stats(statusFlags, &(action->stats));

    // Get number of remaining frames in the current block

    CALLBACK_ASSERT(action->total_frames >= action->done_frames);
    frame_t frames = action->total_frames - action->done_frames;

    if (frameCount < frames)
    {
      frames = frameCount;
    }
    if (frames + offset > frameCount)
    {
      CALLBACK_ASSERT(frameCount > offset);
      frames = frameCount - offset;
    }

    // Shove audio data around

    float* device_data
      = playing ? (float*)output + offset * state->output_channels
                : (float*) input + offset * state->input_channels;

    if (action->type == PLAY_BUFFER || action->type == RECORD_BUFFER)
    {
      float* buffer = action->buffer + action->done_frames * action->channels;
      action->done_frames += frames;
      if (action->type == PLAY_BUFFER)
      {
        while (frames--)
        {
          for (frame_t c = 0; c < action->channels; c++)
          {
            CALLBACK_ASSERT(action->mapping[c] >= 1);
            CALLBACK_ASSERT(action->mapping[c] <= state->output_channels);
            device_data[action->mapping[c] - 1] += *buffer++;
          }
          device_data += state->output_channels;
        }
      }
      else
      {
        CALLBACK_ASSERT(action->type == RECORD_BUFFER);

        while (frames--)
        {
          for (frame_t c = 0; c < action->channels; c++)
          {
            CALLBACK_ASSERT(action->mapping[c] >= 1);
            CALLBACK_ASSERT(action->mapping[c] <= state->input_channels);
            *buffer++ = device_data[action->mapping[c] - 1];
          }
          device_data += state->input_channels;
        }
      }
    }
    else
    {
      CALLBACK_ASSERT(action->type ==   PLAY_RINGBUFFER
                   || action->type == RECORD_RINGBUFFER);

      float* block1 = NULL;
      float* block2 = NULL;
      ring_buffer_size_t size1 = 0;
      ring_buffer_size_t size2 = 0;
      ring_buffer_size_t totalsize = 0;

      if (action->type == PLAY_RINGBUFFER)
      {
        totalsize = PaUtil_GetRingBufferReadRegions(action->ringbuffer
          , (ring_buffer_size_t)frames
          , (void**)&block1, &size1, (void**)&block2, &size2);
        CALLBACK_ASSERT(!totalsize || size1);

        while (size1--)
        {
          for (frame_t c = 0; c < action->channels; c++)
          {
            CALLBACK_ASSERT(action->mapping[c] >= 1);
            CALLBACK_ASSERT(action->mapping[c] <= state->output_channels);
            device_data[action->mapping[c] - 1] += *block1++;
          }
          device_data += state->output_channels;
        }
        while (size2--)
        {
          for (frame_t c = 0; c < action->channels; c++)
          {
            device_data[action->mapping[c] - 1] += *block2++;
          }
          device_data += state->output_channels;
        }
        action->done_frames += (frame_t)totalsize;
        PaUtil_AdvanceRingBufferReadIndex(action->ringbuffer, totalsize);
      }
      else
      {
        CALLBACK_ASSERT(action->type == RECORD_RINGBUFFER);

        totalsize = PaUtil_GetRingBufferWriteRegions(action->ringbuffer
          , (ring_buffer_size_t)frames
          , (void**)&block1, &size1, (void**)&block2, &size2);
        CALLBACK_ASSERT(!totalsize || size1);

        while (size1--)
        {
          for (frame_t c = 0; c < action->channels; c++)
          {
            CALLBACK_ASSERT(action->mapping[c] >= 1);
            CALLBACK_ASSERT(action->mapping[c] <= state->input_channels);
            *block1++ = device_data[action->mapping[c] - 1];
          }
          device_data += state->input_channels;
        }
        while (size2--)
        {
          for (frame_t c = 0; c < action->channels; c++)
          {
            *block2++ = device_data[action->mapping[c] - 1];
          }
          device_data += state->input_channels;
        }
        action->done_frames += (frame_t)totalsize;
        PaUtil_AdvanceRingBufferWriteIndex(action->ringbuffer, totalsize);
      }

      if (totalsize < (ring_buffer_size_t)frames)
      {
        // Ring buffer is empty or full

        // TODO: store some information in action?

        remove_action(actionaddr, state);
        continue;
      }
    }

    // Clean up, prepare next iteration

    if (action->done_frames == action->total_frames)
    {
      remove_action(actionaddr, state);
      continue;
    }
    actionaddr = &(action->next);
  }
  return paContinue;
}
