from graphviz import Digraph
import os
import uuid

def generate_dfa_diagram(states, transitions, finals, name=None):
    try:
        if not name:
            name = f"dfa_{uuid.uuid4().hex}"

        output_dir = "media/diagrams"
        os.makedirs(output_dir, exist_ok=True)

        dot = Digraph(format="png")
        dot.attr(rankdir="LR")

        for state in states:
            if state in finals:
                dot.node(state, shape="doublecircle")
            else:
                dot.node(state)

        for src, symbol, dst in transitions:
            dot.edge(src, dst, label=symbol)

        output_path = os.path.join(output_dir, name)
        dot.render(output_path, cleanup=True)

        return output_path

    except Exception as e:
        print("⚠ Diagram generation failed:", e)
        return None
