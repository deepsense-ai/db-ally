from dbally.audit.events import FallbackEvent


def handle_exception(handle_exception_list):
    def handle_exception_inner(func):
        async def wrapper(self, **kwargs):  # pylint: disable=missing-return-doc
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
