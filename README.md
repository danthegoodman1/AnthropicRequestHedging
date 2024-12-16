# Anthropic Request Hedging Proxy

Simple proxy that works with streamed or non-streamed responses to reduce tail latencies by duplicating the request, and responding with the first one


Tested working with the official python client

## Request hedging benefits

```
[11:37:33.319] INFO (42822): makeRequest completed
    id: "743ef500-b023-4ce4-9972-94285946efb2"
    fetchTimeMS: 473
    stream: true
[11:37:33.320] INFO (42822): request race finished
    id: "743ef500-b023-4ce4-9972-94285946efb2"
    time_taken: 474
    is_streaming: true
    path: "messages"


[11:37:33.783] INFO (42822): makeRequest completed
    id: "743ef500-b023-4ce4-9972-94285946efb2"
    fetchTimeMS: 935
    stream: true
```
