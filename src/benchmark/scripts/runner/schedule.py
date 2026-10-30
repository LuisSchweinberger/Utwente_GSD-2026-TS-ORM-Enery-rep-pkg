"""Complete trials: seed + index, one shared shuffled task order, rotating ORMs."""
from dataclasses import dataclass
from .artifacts import ORMS


@dataclass(frozen=True)
class Task:
    scenario: str
    profile: str


@dataclass(frozen=True)
class Trial:
    index: int
    dataset_seed: int
    orms: tuple
    tasks: tuple

    def rows(self):
        for position, orm in enumerate(self.orms, 1):
            for task_index, task in enumerate(self.tasks, 1):
                yield (self.index, self.dataset_seed, position, orm, task_index, task.scenario, task.profile)


def shuffled_tasks(combinations, seed):
    state = seed
    tasks = [Task(item["scenario"], item["profile"]) for item in combinations]
    for i in range(len(tasks) - 1, 0, -1):
        state = (state ^ (state << 13)) & 0xffffffff
        state ^= state >> 17
        state = (state ^ (state << 5)) & 0xffffffff
        j = int(state / 0x100000000 * (i + 1))
        tasks[i], tasks[j] = tasks[j], tasks[i]
    return tuple(tasks)


def build_schedule(combinations, seed, trials):
    if not 1 <= seed <= 0xffffffff or not 1 <= trials <= 1000 or seed + trials - 1 > 0xffffffff:
        raise ValueError("Seed + trial count exceeds the supported 32-bit seed range")
    return [Trial(index + 1, seed + index, ORMS[index % 3:] + ORMS[:index % 3],
                  shuffled_tasks(combinations, seed + index)) for index in range(trials)]


def write_schedule(path, trials):
    path.parent.mkdir(parents=True, exist_ok=True)
    header = "trial\tdataset_seed\torm_position\torm\ttask_position\tscenario\tprofile\n"
    path.write_text(header + "".join("\t".join(map(str, row)) + "\n" for trial in trials for row in trial.rows()))
