[//]: # "TODO: Compose readme"

# Versioned LRU Cache (Cache with invalidation support)

## Short description/ summary
Versioned_lru_cache_with_ttl is a decorator that can provide versioned lru caching
of function return results.

By being provided with an invalidation function that can determine if the cached
return results have gone stale, the function wrapper will either return the
cached value or rerun the function and return and re-cache the new results in the
case of stale cache.

The idea is that recalculating the work of the function is costly, but there is a
much "cheaper" invalidation function that can tell us when work needs to be redone.

The decorator factory (versioned_lru_cache_with_ttl) also expects being passed a
proxy to a mutable mapping, this proxy should provide a "fresh" version of the
mapping per session. Ex. here being the g request context object used by the Flask
web framework. This allows to calculate the invalidation/ version only once per
session and can make the caching even more efficient.

## Motivation
There a million caveats I want to cover here but I will leave those for the 
section bellow.

The general idea here is that we have some time consuming work that takes place
however there is a much less costly way we can determine if the output of this has
gone stale.

When a requester attempts to access the output of the work we can cheaply check if it
actually needs to be redone or just return the cached work output. 

Additionally we this "version" of the work that is being calculated is also being 
cached on the session object which we expect to be provided by the user of the caching
decorator.

The assumption here is that consistency/ atomicity is expected with in the duration of
the session, so even the calculation of a version/ check if the work output is
invalidated is only done once per session.

As a more concrete example, we can imagine a Flask Webframewok app:
- First flask request handler receives an HTTP request from a client

- As part of the handler the function that needs to do the "expensive" work gets
called since the output of its work is needed to process the request

- Because the function has been decorated with the versioned LRU decorator first
we check if version/ invalidation calculation has been made already and stored on the
global request context "g"

- If the version is already on the request context we know that the "expensive" work
output that is cached can just get returned because we have already check for 
invalidation for this request

- If the version is not available on the request context object "g", we run the
versioning/ invalidation function

- If the cache is not invalidated as a result of the version check we can just return
the work output that is already cached

- If the work output is invalidated the function that does the "expensive" work
is ran and its output is cached, and finally the now update and recached work output
is returned

           Client
             │
             ▼
            ┌──┐
            │..│
           ┌┴──┴┐
           │    │
           │    │
           │    │
           └─┬──┘
             │
             │
         HTTP│Request
             ▼
      ┌────────────────┐
      │                │
      │Flask           │
      │WebFramework    │
      │request handler │
      │                │
      └──────┬─────────┘
             │
             │
             ▼
      ┌────────────────┐
      │                │
      │  Caching       │
      │  Decorator     │
      │                │
      └──────┬─────────┘
             │
             ▼
┌───────────────────────────┐
│                           │
│    Get cached             │
│ version from requet       │         xx
│ context or recalc         │       xx  xx             ┌──────────────────┐
│  the version.             │     xx      xx           │                  │
│                           │   xx          xx         │  Redo expensive  │
│  Aka is existing work     ├─►x  Redo work?  x──Yes──►│  work/ calc.     │
│  output invalidated, do   │   xx          xx         │  Return new      │
│  we need to redo the      │     xx      xx           │  work output     │
│  expensive work           │       xx  xx             │                  │
│                           │         xx               └────────┬─────────┘
│                           │         │                         │
└───────────────────────────┘         │                         ▼
                                      │                ┌──────────────────┐
                                      │                │                  │
                                      │                │                  │
                                      │                │  Cache new work  │
                                     No                │  output          │
                                      │                │                  │
                                      │                └────────┬─────────┘
                                      │                         │
                                      │                         │
                                      │                         │
                                      │                         │
                                      ▼                         │
                            ┌────────────────────┐              │
                            │                    │              │
                            │   Return cached    │              │
                            │   work to Flask    │              │
                            │   which forwards   │◄─────────────┘
                            │   to client        │
                            │                    │
                            └────────────────────┘


## Intended usecase and caveats
There is a lot to be said for the overuse of caching in software engineering as
opposed to structurally fixing systems too often is caching used as a bandaid.

There is of course plenty of valid use cases for caching, I am just not entire sure
there is one for this specific implementation.

The way that this module of code got created was as a prototype of a possible solution
to a work problem. The reality was that along side it I had a some number of other
solutions this one being the least preferred IMO.

Here are some alternatives:
- Can the work output be periodically recalculated by an async task. Is the use case
fine with eventual consistency.

- Can work output instead simply be cached on an external system ex. Redis or even
application operational DB. Can work execution to redo the output be triggered by
some event signifying a state change and/ or invalidation as opposed triggered by
the client request.

We could keep going with possible alternative solutioning here however the point is
that a specific use case should drive solution choice and optimization, that is after
all the actual discipline of engineering, be it only software in this case.

While the use case was not there for me the proto. was too close not to do something
with it, frankly the project setup and all this narration took longer that the actual
programming.

So if happen to:
- Need to check for invalidation on some session request

- The work output can not be eventually consistent

- Want to return the work output as soon as possible even avoiding external systems
and network request lag

- You are OK with an occasional requester getting penalized with a longer processing
time as a trade off that other requesters get almost instant results from the cache

- You want atomicity of the state of the work output across a request/ session

Well then you  might possibly have a use case for this peculiar cache implementation!

## How to setup

## Copy-pastable quick start code example

## Extended example with Flask

## Recommended citation


