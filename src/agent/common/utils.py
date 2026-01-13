from agent.dataclasses.question_tree import QuestionNode, QuestionTree
import random

def get_qa_pairs_from_question_tree(
    question_tree: QuestionTree,
) -> list[dict[str, str]]:
    """
    Take a `QuestionTree` and return a list of question/answer pairs.
    """

    def _get_qa_pairs_from_question_node(
        question_node: QuestionNode,
    ) -> list[dict[str, str]]:
        """
        Take a `QuestionNode` and return a list of question/answer pairs recursively.
        """
        # Type safety check - check if it has the expected attributes
        if (
            not hasattr(question_node, "question")
            or not hasattr(question_node, "answer")
            or not hasattr(question_node, "aspect")
            or not hasattr(question_node, "sub_nodes")
        ):
            raise TypeError(
                f"Expected QuestionNode-like object, got {type(question_node)}: {question_node}"
            )

        qa_pairs = []
        if question_node.answer:
            qa_pairs.append(
                {"question": question_node.question, "answer": question_node.answer, "aspect": question_node.aspect}
            )
        for node in question_node.sub_nodes:
            qa_pairs.extend(_get_qa_pairs_from_question_node(node))
        return qa_pairs

    qa_pairs = []
    qa_pairs.extend(_get_qa_pairs_from_question_node(question_tree.root_node))

    return qa_pairs

def get_qa_pair_from_question_tree_with_index(
    question_tree: QuestionTree,
    index: int
) -> dict[str, str]:
    """
    Take a `QuestionTree` and return a question/answer pair at the given index
    """
    qa_pairs = get_qa_pairs_from_question_tree(question_tree)
    return qa_pairs[index]

def format_qa_pairs_with_index(qa_pairs: list[dict[str, str]]) -> str:
    """
    Format a list of question/answer pairs into a string with index.
    """
    return "\n".join(
        [f"{i}: {qa['question']}\n{qa['answer']}" for i, qa in enumerate(qa_pairs)]
    )


def format_qa_pairs_without_index(qa_pairs: list[dict[str, str]]) -> str:
    """
    Format a list of question/answer pairs into a string without index.
    """
    return "\n".join([f"{qa['question']}\n{qa['answer']}" for qa in qa_pairs])


def merge_question_trees(question_trees: list[QuestionTree]) -> QuestionTree:
    """
    Merge a list of question trees into a single question tree.
    Preserves each tree's root node (with its answer) as a sub-node of the merged tree.
    """
    root_node = QuestionNode(
        question="Should we invest in this company?", answer="", sub_nodes=[], aspect="final"
    )

    # Randomly shuffle the question trees
    random.shuffle(question_trees)

    for question_tree in question_trees:
        # Add the entire root node (with its answer) as a sub-node
        root_node.sub_nodes.append(question_tree.root_node)
    return QuestionTree(aspect="final", root_node=root_node)

if __name__ == "__main__":
    from agent.cached_answered_question_trees import get_brandback_answered_question_tree, get_aily_labs_answered_question_tree

    brandback_question_tree = get_brandback_answered_question_tree()
    aily_labs_question_tree = get_aily_labs_answered_question_tree()

    merged_question_tree = merge_question_trees([aily_labs_question_tree, brandback_question_tree])
    print(merged_question_tree.model_dump_json(indent=4))
