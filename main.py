from enum import Enum
import matplotlib.pyplot as plt


class AlarmState(str, Enum):
    LOW_LOW = "LOW_LOW"
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    HIGH_HIGH = "HIGH_HIGH"


class Mode(str, Enum):
    FILL = "FILL"
    DRAIN = "DRAIN"


def trigger_alarm(level, low_low_limit, low_limit, high_limit, high_high_limit):
    if level <= low_low_limit:
        return AlarmState.LOW_LOW
    elif level <= low_limit:
        return AlarmState.LOW
    elif level >= high_high_limit:
        return AlarmState.HIGH_HIGH
    elif level >= high_limit:
        return AlarmState.HIGH
    return AlarmState.NORMAL


def control_logic(mode, alarm):
    if alarm == AlarmState.LOW or alarm == AlarmState.LOW_LOW:
        mode = Mode.FILL
    elif alarm == AlarmState.HIGH or alarm == AlarmState.HIGH_HIGH:
        mode = Mode.DRAIN

    if mode == Mode.FILL:
        pump_state = 1
        valve_state = 0
    else:
        pump_state = 0
        valve_state = 1

    return mode, pump_state, valve_state


def calculate_flows(pump_state, valve_state, pump_flow_rate, valve_flow_rate):
    inlet_flow = pump_flow_rate if pump_state == 1 else 0.0
    outlet_flow = valve_flow_rate if valve_state == 1 else 0.0
    return inlet_flow, outlet_flow


def update_level(level, inlet_flow, outlet_flow, dt, tank_height):
    level = level + (inlet_flow - outlet_flow) * dt
    level = max(0.0, min(level, tank_height))
    return level


def display_status(time_step, level, alarm, mode, pump_state, valve_state, inlet_flow, outlet_flow):
    print(
        f"Time: {time_step:>3}s | "
        f"Level: {level:>5.2f} m | "
        f"Alarm: {alarm.value:>8} | "
        f"Mode: {mode.value:>5} | "
        f"Pump: {pump_state} | "
        f"Valve: {valve_state} | "
        f"Inlet: {inlet_flow:.2f} | "
        f"Outlet: {outlet_flow:.2f}"
    )


def plot_level_history(time_history, level_history, low_limit, high_limit, low_low_limit, high_high_limit):
    plt.figure(figsize=(10, 5))
    plt.plot(time_history, level_history, marker="o")
    plt.axhline(low_low_limit, linestyle="--", label="Low-Low Limit")
    plt.axhline(low_limit, linestyle="--", label="Low Limit")
    plt.axhline(high_limit, linestyle="--", label="High Limit")
    plt.axhline(high_high_limit, linestyle="--", label="High-High Limit")
    plt.xlabel("Time (s)")
    plt.ylabel("Tank Level (m)")
    plt.title("Tank Level Simulation")
    plt.legend()
    plt.grid(True)
    plt.show()


def main():
    tank_height = 15.0
    level = 2.0
    dt = 1.0
    simulation_time = 120

    pump_flow_rate = 0.35
    valve_flow_rate = 0.30

    low_low_limit = 0.5
    low_limit = 1.0
    high_limit = 14.0
    high_high_limit = 14.5

    mode = Mode.FILL

    time_history = []
    level_history = []

    for t in range(simulation_time + 1):
        alarm = trigger_alarm(level, low_low_limit, low_limit, high_limit, high_high_limit)
        mode, pump_state, valve_state = control_logic(mode, alarm)
        inlet_flow, outlet_flow = calculate_flows(pump_state, valve_state, pump_flow_rate, valve_flow_rate)

        display_status(t, level, alarm, mode, pump_state, valve_state, inlet_flow, outlet_flow)

        time_history.append(t)
        level_history.append(level)

        level = update_level(level, inlet_flow, outlet_flow, dt, tank_height)

    plot_level_history(time_history, level_history, low_limit, high_limit, low_low_limit, high_high_limit)


if __name__ == "__main__":
    main()