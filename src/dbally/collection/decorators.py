from typing import Callable

from dbally.audit.events import FallbackEvent


# pylint: disable=protected-access
def handle_exception(handle_exception_list) -> Callable:
    """
    Decorator to handle specified exceptions during the execution of an asynchronous function.

    This decorator is designed to be used with class methods, and it handles exceptions specified
    in `handle_exception_list`. If an exception occurs and a fallback collection is available,
    it will attempt to perform the same operation using the fallback collection.

    Args:
        handle_exception_list (tuple): A tuple of exception classes that should be handled
                                       by this decorator.

    Returns:
        function: A wrapper function that handles the specified exceptions and attempts a fallback
                  operation if applicable.

    Example:
        @handle_exception((SomeException, AnotherException))
        async def some_method(self, **kwargs):
            # method implementation

    The decorated method can expect the following keyword arguments in `kwargs`:
        - question (str): The question to be asked.
        - dry_run (bool): Whether to perform a dry run.
        - return_natural_response (bool): Whether to return a natural response.
        - llm_options (dict): Options for the language model.
        - event_tracker (EventTracker): An event tracker instance.

    If an exception is caught and a fallback collection is available, an event of type
    `FallbackEvent` will be tracked, and the fallback collection's `ask` method will be called
    with the same arguments.

    Raises:
        Exception: If an exception in `handle_exception_list` occurs and no fallback collection is
                   available, the original exception is re-raised.
    """

    def handle_exception_inner(func: Callable) -> Callable:  # pylint: disable=missing-return-doc
        async def wrapper(self, **kwargs) -> Callable:  # pylint: disable=missing-return-doc
            try:
                result = await func(self, **kwargs)
            except handle_exception_list as error:
                question = kwargs.get("question")
                dry_run = kwargs.get("dry_run")
                return_natural_response = kwargs.get("return_natural_response")
                llm_options = kwargs.get("llm_options")
                selected_view_name = str(kwargs.get("selected_view_name"))
                event_tracker = kwargs.get("event_tracker")

                if self._fallback_collection:
                    event = FallbackEvent(
                        triggering_collection_name=self.name,
                        triggering_view_name=selected_view_name,
                        fallback_collection_name=self._fallback_collection.name,
                        error_description=repr(error),
                    )
                    if not self.fallback_collection_chain:
                        self.fallback_collection_chain = []
                    else:
                        self._fallback_collection.append(self._fallback_collection)

                    async with event_tracker.track_event(event) as span:
                        result = await self._fallback_collection.ask(
                            question=question,
                            dry_run=dry_run,
                            return_natural_response=return_natural_response,
                            llm_options=llm_options,
                        )
                        span(event)

                else:
                    raise error

            return result

        return wrapper

    return handle_exception_inner
