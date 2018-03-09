# Controlling Your Experiment

The UE and all of the OAI services can be controlled from the command
line by logging into the appropriate nodes. In addition, all nodes in
the experiment can be rebooted or reloaded (reload means loading a
fresh disk image wiping out any changes) from the portal
interface. After any reboot, all services will automatically start and
the UE should attach and connect to provide end-to-end connectivity.

## UE Control

Log into the `adb-tgt` node on your experiment. This node links to the
UE via an adb proxy with this command:

    pnadb -a

Sometimes just after rebooting this command will fail to connect. If
so, try running it again after a few minutes. If it persists, you can
reboot or reload (reload means loading a fresh disk image) the UE and
try connecting again once it is complete.

You can log into the UE using adb:

    adb shell

From there, you can manipulate or run any system on the phone. To see
if there is end to end connectivity, try `ping 8.8.8.8` for example.

The adb node can be rebooted from the command line with:

    adb reboot

Any other adb command can be run as well.

## eNodeB Control

The startup script on the `enb1` node always waits for the EPC node
and then starts the enb service when booting. You can start the enb
service by hand by running:

    sudo /local/repository/bin/enb.start.sh

Or you can kill a running enb service with:

    sudo /local/repository/bin/enb.kill.sh

The enb service should be started last because if it doesn't detect an
mme when it starts, it will never connect.

## Simulated UE+eNB control

When the experiment starts, necessary scripts are started with the required
configurations. You can monitor the logs by attaching to the screen:
  
    sudo screen -r sim_enb

To confirm if UE is connected, ping using the oip1 interface:

    ping -I oip1 8.8.8.8

To restart oaisim, use:

    sudo /local/repository/bin/config_oai.pl -r SIM_ENB

The code for oaisim can be found in `/opt/oai/openairinterface5g`.
You can build the latest version of the code by using following steps:

    cd ~
    git clone https://gitlab.eurecom.fr/oai/openairinterface5g.git
    cd openairinterface5g
    source oaienv
    cd cmake_targets
    ./build_oai -I  --oaisim -x --install-system-files
    ./build_oai --oaisim -c
    cd tools
    sudo ./run_enb_ue_virt_s1 -c <conf_file>

You can use the config file `/usr/local/etc/oai/enb.conf` and update any
necessary parameters like interfaces, MCC, MNC etc.
Please note that current profile has been tested with the default binaries
and not with other versions of OAI.

## EPC Control

The startup script on the `epc` boots up the hss, mme, and spgw
services. After all three of these are started, it syncronises with
the startup script on the `enb1`. To manually start any of these
services, run one of these scripts on the `epc` node:

    sudo /local/repository/bin/hss.start.sh
    sudo /local/repository/bin/mme.start.sh
    sudo /local/repository/bin/spgw.start.sh

When starting them all by hand, make sure to start them in that order.

To kill these scripts, just run one of these on the `epc` node:

    sudo /local/repository/bin/hss.kill.sh
    sudo /local/repository/bin/mme.kill.sh
    sudo /local/repository/bin/spgw.kill.sh

## Restarting without rebooting

If you want to restart all the services but don't want to reboot the
nodes themselves, you can first kill all services, then on the `enb1`
node, run:

    sudo /local/repository/bin/config_oai.pl -r ENB

And on the `epc` node, run:

    sudo /local/repository/bin/config_oai.pl -r EPC

## Tweaking Configuration

The source templates for the configuration files are at
`/local/repository/etc/*.conf`. These are used only once when the
experiment boots for the first time. They in turn generate the
configuration files which are located at `/usr/local/etc/oai/*.conf`
on both the `epc` and `enb1` nodes. The generated configuration files
can be modified, but those changes will be lost if the node is
reloaded, the experiment ends, or you force them to be regenerated
from the templates.

To change configuration permanently, you will want to fork the
repository for this profile, make a copy of it, and change the
configuration files in your forked repo.
