from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from core.controller import PIDController
from core.logging_utils import save_simulation_to_csv
from core.plotting import plot_tank_pi_results


@dataclass
class TankParameters:
    area_m2: float = 1.0
    max_level_m: float = 15.0
    base_outflow_m3s: float = 0.15
    outlet_gain_m3s_per_m: float = 0.03
    max_inflow_m3s: float = 0.40


@dataclass
class SimulationParameters:
    dt_s: float = 1.0
    duration_s: int = 600
    initial_level_m: float = 2.0
    setpoint_m: float = 8.0
    csv_filename: str = "data/generated/tank_pi_simulation.csv"
    add_measurement_noise: bool = False
    noise_std_dev_m: float = 0.0
    random_seed: int = 42


def calculate_outflow(level_m: float, tank: TankParameters) -> float:
    """
    Simple self-regulating outlet model.
    Outflow increases with tank level, which makes the process easier to control
    with PI than a purely integrating tank.
    """
    outflow = tank.base_outflow_m3s + tank.outlet_gain_m3s_per_m * level_m
    return max(0.0, outflow)


def apply_measurement_noise(
    true_level_m: float,
    rng: np.random.Generator,
    noise_std_dev_m: float,
    add_noise: bool,
) -> float:
    if not add_noise:
        return true_level_m
    return true_level_m + rng.normal(0.0, noise_std_dev_m)


def update_tank_level(
    level_m: float,
    inflow_m3s: float,
    outflow_m3s: float,
    dt_s: float,
    tank: TankParameters,
) -> float:
    """
    Level update from volume balance:
        dV/dt = Qin - Qout
        dH/dt = (Qin - Qout) / Area
    """
    dlevel = ((inflow_m3s - outflow_m3s) / tank.area_m2) * dt_s
    new_level = level_m + dlevel
    return float(np.clip(new_level, 0.0, tank.max_level_m))


def run_tank_pi_simulation(
    tank: TankParameters,
    sim: SimulationParameters,
    controller: PIDController,
) -> list[dict]:
    rng = np.random.default_rng(sim.random_seed)

    level_m = sim.initial_level_m
    results: list[dict] = []

    n_steps = int(sim.duration_s / sim.dt_s) + 1

    for step in range(n_steps):
        time_s = step * sim.dt_s

        measured_level_m = apply_measurement_noise(
            true_level_m=level_m,
            rng=rng,
            noise_std_dev_m=sim.noise_std_dev_m,
            add_noise=sim.add_measurement_noise,
        )

        error_m = sim.setpoint_m - measured_level_m

        controller_output_pct = controller.update(
            setpoint=sim.setpoint_m,
            measurement=measured_level_m,
            dt=sim.dt_s,
        )

        inflow_m3s = (controller_output_pct / 100.0) * tank.max_inflow_m3s
        outflow_m3s = calculate_outflow(level_m, tank)

        results.append(
            {
                "time_s": time_s,
                "setpoint_m": sim.setpoint_m,
                "true_level_m": level_m,
                "measured_level_m": measured_level_m,
                "error_m": error_m,
                "controller_output_pct": controller_output_pct,
                "inflow_m3s": inflow_m3s,
                "outflow_m3s": outflow_m3s,
            }
        )

        level_m = update_tank_level(
            level_m=level_m,
            inflow_m3s=inflow_m3s,
            outflow_m3s=outflow_m3s,
            dt_s=sim.dt_s,
            tank=tank,
        )

    return results


def main() -> None:
    tank = TankParameters(
        area_m2=1.0,
        max_level_m=15.0,
        base_outflow_m3s=0.15,
        outlet_gain_m3s_per_m=0.03,
        max_inflow_m3s=0.40,
    )

    sim = SimulationParameters(
        dt_s=1.0,
        duration_s=600,
        initial_level_m=2.0,
        setpoint_m=8.0,
        csv_filename="data/generated/tank_pi_simulation.csv",
        add_measurement_noise=False,
        noise_std_dev_m=0.01,
        random_seed=42,
    )

    controller = PIDController(
        kp=8.0,
        ki=0.08,
        kd=0.0,
        output_min=0.0,
        output_max=100.0,
    )

    results = run_tank_pi_simulation(
        tank=tank,
        sim=sim,
        controller=controller,
    )

    output_path = Path(sim.csv_filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    save_simulation_to_csv(results, output_path)

    plot_tank_pi_results(results)

    print(f"Saved simulation results to: {output_path}")


if __name__ == "__main__":
    main()