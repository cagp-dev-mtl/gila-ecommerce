from pydantic import BaseModel, ConfigDict


class BaseContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    graceful_exit: bool = False


class BaseStep:
    def execute(self, context: BaseContext) -> BaseContext:
        raise NotImplementedError


def run_pipeline(steps: tuple[BaseStep, ...], context: BaseContext) -> BaseContext:
    for step in steps:
        if context.graceful_exit:
            break
        context = step.execute(context)
    return context
