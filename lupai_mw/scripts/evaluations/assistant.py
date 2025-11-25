import heapq
import asyncio

from rich.pretty import pprint
from langchain_openai import ChatOpenAI

from ragas import evaluate
from ragas import EvaluationDataset
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import LLMContextPrecisionWithoutReference

from common.logger import get_logger
from lupai_mw.db import MongoConnector


logger = get_logger(__name__)


async def main() -> None:
    llm = ChatOpenAI(model="gpt-4.1-mini")
    evaluator_llm = LangchainLLMWrapper(llm)

    mongo_connector = MongoConnector()
    assistant_states = [
        state
        async for state in mongo_connector.find_multiple(
            collection="states",
            query_filter={
                "answer_status": "success",
            },
        )
    ]

    evaluation_items = [
        {
            "_id": state["_id"],
            "user_input": state["query"],
            "retrieved_contexts": [
                rc["text"] for rc in state["relevant_chunks"]
            ],
            "response": state["assistant_response"],
        }
        for state in assistant_states
    ]

    evaluation_dataset = EvaluationDataset.from_list(evaluation_items)
    logger.info(f"eval_items: {len(evaluation_dataset)}")

    result = evaluate(
        dataset=evaluation_dataset,
        metrics=[LLMContextPrecisionWithoutReference()],
        llm=evaluator_llm,
        show_progress=True,
        batch_size=10,
    )

    scores = result["llm_context_precision_without_reference"]
    avg_score = sum(scores) / len(scores)
    worst_indices = heapq.nsmallest(
        10,
        range(len(scores)),
        key=scores.__getitem__,
    )

    display_results = {
        "avg_score": avg_score,
        "worst_scores": [
            {
                "_id": evaluation_items[idx]["_id"],
                "score": scores[idx],
            }
            for idx in worst_indices
        ],
    }

    pprint(display_results)


if __name__ == "__main__":
    asyncio.run(main())
