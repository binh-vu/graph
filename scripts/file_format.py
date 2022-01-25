import os
import shutil
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List
from loguru import logger


class FileStructure:
    def __init__(self, infile: str, klass: str, indent="    ") -> None:
        self.infile = infile
        with open(infile, "r") as f:
            self.lines = f.readlines()

        # detect where the class starts
        self.klass_start = 0
        for i, line in enumerate(self.lines):
            if line.startswith(f"class {klass}"):
                self.klass_start = i
                if line.find("(") != -1 and line.find(")") == -1:
                    # class is not closed
                    while self.lines[self.klass_start].find(")") == -1:
                        self.klass_start += 1
                self.klass_start += 1
                break

        self.klass_end = len(self.lines)
        for i in range(self.klass_start, len(self.lines)):
            if self.lines[i].strip() == "" or self.lines[i].startswith(indent):
                continue
            self.klass_end = i
            break

        self.funcs = []
        for i in range(self.klass_start, self.klass_end):
            line = self.lines[i]
            if line.startswith(f"{indent}def "):
                # this is where the function begin, look before and after
                func_start = i
                while True:
                    if self.lines[func_start - 1].strip() == "" or not (
                        self.lines[func_start - 1].startswith(indent)
                        and not self.lines[func_start - 1].startswith(indent * 2)
                    ):
                        break
                    func_start -= 1

                # detect if the function is not closed yet
                if re.match(rf"{indent}def [^(]+\([^)]*\n", line) is not None:
                    # the function is not closed yet
                    func_end = i + 1
                    while True:
                        if self.lines[func_end].find(")") != -1:
                            func_end += 1
                            break
                        func_end += 1
                else:
                    func_end = i + 1

                while func_end < len(self.lines):
                    if (
                        not self.lines[func_end].startswith(f"{indent}{indent}")
                        and self.lines[func_end].strip() != ""
                    ):
                        break
                    func_end += 1

                self.funcs.append(
                    {
                        "name": re.match(rf"{indent}def +([^(]+)\(", line).group(1),
                        "start": func_start,
                        "end": func_end,
                    }
                )

        # make sure it has some functions
        assert len(self.funcs) > 0

        # adjust the start & end of the class
        self.klass_start = min([x["start"] for x in self.funcs]) - 1
        self.klass_end = max([x["end"] for x in self.funcs])

    def reorder_funcs(self, new_order: List[str]) -> None:
        # current implementation works only for functions with empty lines between them
        used_lines = set()
        for func in self.funcs:
            for i in range(func["start"], func["end"]):
                used_lines.add(i)
        for i in range(self.klass_start + 1, self.klass_end):
            if i not in used_lines:
                assert self.lines[i].strip() == "", f"Line {i}: {self.lines[i]}"

        new_lines = self.lines[: self.klass_start + 1]
        funcs = {x["name"]: x for x in self.funcs}
        if set(funcs.keys()) != set(new_order):
            logger.error(
                "Missing functions: {}", set(funcs.keys()).difference(new_order)
            )
            logger.error("Extra functions: {}", set(new_order).difference(funcs.keys()))
            raise ValueError("Invalid order")

        for func in new_order:
            new_lines += self.lines[funcs[func]["start"] : funcs[func]["end"]]
            new_lines.append("\n")
        new_lines += self.lines[self.klass_end :]

        backup = f"{self.infile}.{datetime.now().isoformat()}"
        assert not os.path.exists(backup), backup
        shutil.copyfile(self.infile, backup)
        with open(self.infile, "w") as f:
            for line in new_lines:
                f.write(line)

    def sync_with(self, fs: "FileStructure") -> None:
        """Make your functions following the same order as in the other file.
        The functions that are not in the other file are put at the bottom"""
        old_order = [x["name"] for x in self.funcs]
        new_order = []
        if self.has_func("__init__") and not fs.has_func("__init__"):
            new_order.append("__init__")
            old_order.pop(old_order.index("__init__"))

        for func in fs.funcs:
            if func["name"] not in old_order:
                continue
            new_order.append(func["name"])
            old_order.pop(old_order.index(func["name"]))
        new_order += old_order
        assert len(new_order) == len(self.funcs)
        self.reorder_funcs(new_order)

    def has_func(self, name: str):
        return any(name == x["name"] for x in self.funcs)


if __name__ == "__main__":
    fs = FileStructure("/workspace/sm-dev/graph/graph/interface.py", "IGraph")
    fs2 = FileStructure(
        "/workspace/sm-dev/graph/graph/retworkx/digraph.py", "_RetworkXDiGraph"
    )
    fs3 = FileStructure(
        "/workspace/sm-dev/graph/graph/retworkx/str_digraph.py", "RetworkXStrDiGraph"
    )
    # fs2.sync_with(fs)
    fs3.sync_with(fs)

    # print(len(fs.funcs))
    # print([f["name"] for f in fs.funcs])
    # fs.reorder_funcs(
    #     [
    #         "num_nodes",
    #         "nodes",
    #         "iter_nodes",
    #         "filter_nodes",
    #         "iter_filter_nodes",
    #         "has_node",
    #         "get_node",
    #         "add_node",
    #         "remove_node",
    #         "update_node",
    #         "find_node",
    #         "degree",
    #         "in_degree",
    #         "out_degree",
    #         "successors",
    #         "predecessors",
    #         "num_edges",
    #         "edges",
    #         "iter_edges",
    #         "filter_edges",
    #         "iter_filter_edges",
    #         "has_edge",
    #         "get_edge",
    #         "add_edge",
    #         "update_edge",
    #         "remove_edge",
    #         "remove_edge_between_nodes",
    #         "remove_edges_between_nodes",
    #         "has_edge_between_nodes",
    #         "has_edges_between_nodes",
    #         "get_edge_between_nodes",
    #         "get_edges_between_nodes",
    #         "in_edges",
    #         "out_edges",
    #         "group_in_edges",
    #         "group_out_edges",
    #         "subgraph_from_edges",
    #         "subgraph_from_edge_triples",
    #         "copy",
    #         "check_integrity",
    #     ]
    # )
    # print([x["name"] for x in fs2.funcs])
