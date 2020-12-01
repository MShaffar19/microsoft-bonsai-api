#!/usr/bin/env python
"""
Microsoft-Bonsai-API integration with House Energy Simulator
"""

import os
import time
from distutils.util import strtobool
from typing import Any, Dict, List

from dotenv import load_dotenv, set_key
from microsoft_bonsai_api.simulator.client import BonsaiClient, BonsaiClientConfig
from microsoft_bonsai_api.simulator.generated.models import (
    SimulatorInterface,
    SimulatorState,
)

from policies import random_policy
from sim import house_simulator

dir_path = os.path.dirname(os.path.realpath(__file__))


class TemplateSimulatorSession:
    def __init__(
        self, modeldir: str = "sim", render: bool = False, env_name: str = "HouseEnergy"
    ):
        """Template for simulating sessions with microsoft_bonsai_api

        Parameters
        ----------
        modeldir: str, optional
            directory where you sim folder lives
        render: bool, optional
            render the current iteration
        env_name: str, optional
            name of simulator environment, registered by SimulatorInterface 
        """

        self.modeldir = modeldir
        self.env_name = env_name
        print("Using simulator file from: ", os.path.join(dir_path, self.modeldir))
        self.default_config = {
            "K": 0.5,
            "C": 0.3,
            "Qhvac": 9,
            "Tin_initial": 30,
            "schedule_index": 2,
            "number_of_days": 1,
            "timestep": 5,
            "max_iterations": int(1 * 24 * 60 / 5),
        }
        self._reset()
        self.terminal = False
        self.render = render

    def get_state(self) -> Dict[str, float]:
        """ Called to retreive the current state of the simulator. """

        sim_state = {
            "Tset": float(self.simulator.Tset),
            "Tset1": float(self.simulator.Tset1),  # forecast at +1 iteration
            "Tset2": float(self.simulator.Tset2),  # forecast at +2 iterations
            "Tset3": float(self.simulator.Tset3),  # forecast at +3 iterations
            "Tin": float(self.simulator.Tin),
            "Tout": float(self.simulator.Tout),
            "power": float(self.simulator.get_Power()),
        }

        return sim_state

    def _reset(self, config: dict = None):
        """Helper function for resetting a simulator environment

        Parameters
        ----------
        config : dict, optional
            [description], by default None
        """

        if config:
            self.sim_config = config
        else:
            self.sim_config = self.default_config

        self.simulator = house_simulator.House(
            K=self.sim_config["K"],
            C=self.sim_config["C"],
            Qhvac=self.sim_config["Qhvac"],
            Tin_initial=self.sim_config["Tin_initial"],
        )
        self.simulator.setup_schedule(
            days=self.sim_config["number_of_days"],
            timestep=self.sim_config["timestep"],
            schedule_index=self.sim_config["schedule_index"],
            max_iterations=288,
        )

    def episode_start(self, config: Dict[str, Any] = None):
        """Method invoked at the start of each episode with a given 
        episode configuration.

        Parameters
        ----------
        config : Dict[str, Any]
            SimConfig parameters for the current episode defined in Inkling
        """

        self._reset(config)

    def episode_step(self, action: Dict[str, Any]):
        """Called for each step of the episode 

        Parameters
        ----------
        action : Dict[str, Any]
            BrainAction chosen from the Bonsai Service, prediction or exploration
        """

        self.simulator.update_hvacON(action["hvacON"])
        self.simulator.update_Tin()
        if self.render:
            self.sim_render()

    def sim_render(self):

        if self.render:
            self.simulator.show()

    def halted(self) -> bool:
        """Should return True if the simulator cannot continue"""
        return self.terminal

    def random_policy(self, state: Dict = None) -> Dict:

        return random_policy()


def env_setup():
    """Helper function to setup connection with Project Bonsai

    Returns
    -------
    Tuple
        workspace, and access_key
    """

    load_dotenv(verbose=True)
    workspace = os.getenv("SIM_WORKSPACE")
    access_key = os.getenv("SIM_ACCESS_KEY")

    env_file_exists = os.path.exists(".env")
    if not env_file_exists:
        open(".env", "a").close()

    if not all([env_file_exists, workspace]):
        workspace = input("Please enter your workspace id: ")
        set_key(".env", "SIM_WORKSPACE", workspace)
    if not all([env_file_exists, access_key]):
        access_key = input("Please enter your access key: ")
        set_key(".env", "SIM_ACCESS_KEY", access_key)

    load_dotenv(verbose=True, override=True)
    workspace = os.getenv("SIM_WORKSPACE")
    access_key = os.getenv("SIM_ACCESS_KEY")

    return workspace, access_key


def test_random_policy(num_episodes: int = 10, render: bool = False):
    """Test a policy using random actions over a fixed number of episodes

    Parameters
    ----------
    num_episodes : int, optional
        number of iterations to run, by default 10
    """

    sim = TemplateSimulatorSession(render=render)
    for episode in range(num_episodes):
        iteration = 0
        terminal = False
        obs = sim.episode_start()
        while not terminal:
            action = sim.random_policy()
            sim.episode_step(action)
            sim_state = sim.get_state()
            print(f"Running iteration #{iteration} for episode ${episode}")
            print(f"Observations: {sim_state}")
            iteration += 1


def main(render: bool = False, config_setup: bool = False):
    """Main entrypoint for running simulator connections

    Parameters
    ----------
    render : bool, optional
        visualize steps in environment, by default True, by default False
    """

    # workspace environment variables
    if config_setup:
        env_setup()
        load_dotenv(verbose=True, override=True)

    # Grab standardized way to interact with sim API
    sim = TemplateSimulatorSession(render=render)

    # Configure client to interact with Bonsai service
    config_client = BonsaiClientConfig()
    client = BonsaiClient(config_client)

    # # Load json file as simulator integration config type file
    # with open("interface.json") as file:
    #     interface = json.load(file)

    # Create simulator session and init sequence id
    registration_info = SimulatorInterface(
        name=sim.env_name,
        timeout=60,
        simulator_context=config_client.simulator_context,
    )
    registered_session = client.session.create(
        workspace_name=config_client.workspace, body=registration_info
    )
    print("Registered simulator.")
    sequence_id = 1

    try:
        while True:
            # Advance by the new state depending on the event type
            sim_state = SimulatorState(
                sequence_id=sequence_id, state=sim.get_state(), halted=sim.halted(),
            )
            event = client.session.advance(
                workspace_name=config_client.workspace,
                session_id=registered_session.session_id,
                body=sim_state,
            )
            sequence_id = event.sequence_id
            print("[{}] Last Event: {}".format(time.strftime("%H:%M:%S"), event.type))

            # Event loop
            if event.type == "Idle":
                time.sleep(event.idle.callback_time)
                print("Idling...")
            elif event.type == "EpisodeStart":
                sim.episode_start(event.episode_start.config)
            elif event.type == "EpisodeStep":
                sim.episode_step(event.episode_step.action)
            elif event.type == "EpisodeFinish":
                print("Episode Finishing...")
            elif event.type == "Unregister":
                client.session.delete(
                    workspace_name=config_client.workspace,
                    session_id=registered_session.session_id,
                )
                print("Unregistered simulator.")
            else:
                pass
    except KeyboardInterrupt:
        # Gracefully unregister with keyboard interrupt
        client.session.delete(
            workspace_name=config_client.workspace,
            session_id=registered_session.session_id,
        )
        print("Unregistered simulator.")
    except Exception as err:
        # Gracefully unregister for any other exceptions
        client.session.delete(
            workspace_name=config_client.workspace,
            session_id=registered_session.session_id,
        )
        print("Unregistered simulator because: {}".format(err))


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Bonsai and Simulator Integration...")
    parser.add_argument(
        "--render",
        type=lambda x: bool(strtobool(x)),
        default=False,
        help="Render training episodes",
    )
    parser.add_argument(
        "--log-iterations",
        type=lambda x: bool(strtobool(x)),
        default=False,
        help="Log iterations during training",
    )
    parser.add_argument(
        "--config-setup",
        type=lambda x: bool(strtobool(x)),
        default=False,
        help="Use a local environment file to setup access keys and workspace ids",
    )
    parser.add_argument(
        "--test-local",
        type=lambda x: bool(strtobool(x)),
        default=False,
        help="Run simulator locally without connecting to platform",
    )

    args = parser.parse_args()

    if args.test_local:
        test_random_policy(render=args.render, num_episodes=1)
    else:
        main(config_setup=args.config_setup, render=args.render)

