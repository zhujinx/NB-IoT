# EXPERIMENTAL PROFILE TO TEST SDR UE

# About This Profile

Be sure to setup your SSH keys as outlined in the manual; it's better
to log in via a real SSH client to the nodes in your experiment.

The Open Air Interface source is located under `/opt/oai` on the enb1
and epc nodes.  It is mounted as a clone of a remote blockstore
(dataset) maintained by PhantomNet.  Feel free to change anything in
here, but be aware that your changes will not persist when your
experiment terminates.

This experiment can work in two modes:
1. UE and eNodeB SDR
2. Simulated UE+eNodeB (OAISIM).

To enable OAISIM, select OAI_SIM in the drop down menu "Experiment Type"
while instantiating the experiment. When the experiment starts, two nodes
will be created: sim_enb and epc.

To get the SDR based eNodeB and off-the-shelf UE, select one of the other
two options in the "Experiment Type" based upon the requirements.

# Getting Started

After booting is complete, log onto either the `enb1` or `epc`
nodes. From there, you will be able to start all OAI services across
the network by running:

    sudo /local/repository/bin/start_oai.pl

This will stop any currently running OAI services, start all services
(both epc and enodeb) again, and then interactively show a tail of the
logs of the mme and enodeb services. Once you see the logs, you can
exit at any time with Ctrl-C, but the services stay running in the
background and save logs to `/var/log/oai/*` on the `enb1` and `epc`
nodes.

When using real UE, to access the UE via ADB, first log in to the `adb-tgt`
node, then run `pnadb -a` to connect to the UE.  Use ADB commands as per
normal afterward.  If/when you reboot the UE, be aware that you will need
to again run `pnadb -a` to reestablish the ADB connection; wait a minute
or so for the UE to become available again before doing this.

The OAI mobile networking functions should automatically start up when
your experiment starts up.  You can pull up and monitor the OAI
processes on the `epc` and `enb1` nodes. Execute `sudo screen -ls` to
see what sessions are available. The commands for controlling services
on these nodes are located in `/local/repository/bin`.

OAI is a project that is in development. As such, it is not always
stable and there will be times when it gets into a failed state that
it can never recover from. Almost always, you will be able to bring
things back by either rebooting the experiment from the portal or
restarting the services by hand from the command line.

For more detailed information:

  * [Controlling OAI](https://gitlab.flux.utah.edu/powder-profiles/OAI-Real-Hardware/blob/master/control.md)
  * [Inspecting OAI](https://gitlab.flux.utah.edu/powder-profiles/OAI-Real-Hardware/blob/master/inspect.md)
  * [Modifying OAI](https://gitlab.flux.utah.edu/powder-profiles/OAI-Real-Hardware/blob/master/modify.md)
  * [Modifying This Profile](https://gitlab.flux.utah.edu/powder-profiles/OAI-Real-Hardware/blob/master/modify-profile.md)
