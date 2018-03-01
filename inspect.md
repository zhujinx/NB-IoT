# Inspecting Your Experiment

There are a lot of moving parts in an OAI system. In order to see them
all going at once, it is best to have multiple vantage points into the
system.

## Inspecting the UE

The UE is a Nexus 5 running a vanilla Android. Currently, you are able
to interact and inspect the UE using adb from the `adb-tgt` node. Once
you log into the `adb-tgt` node, you first need to make sure that the
adb is connected to the UE through our proxy. 

    pnadb -a

Sometimes just after rebooting this command will fail to connect. If
so, try running it again after a few minutes. If it persists, you can
reboot or reload (reload means loading a fresh disk image) the UE and
try connecting again once it is complete.

Once connected through the proxy, almost any adb command will
work. You can log into the UE with:

    adb shell

You can inspect its device logs as well. Most usefully, you can see its radio log:

    adb logcat -b radio

## Startup Scripts

The startup script at `/local/repository/config_oai.pl` runs on both
the `epc` and `enb1` nodes. In both cases, it logs its progress to
`/var/log/oai/startup.log`. You can see there what it is doing and
whether it has started up the services.

## Inspecting the eNodeB

The eNodeB is an Intel NUC connected to a USRP software-defined
radio. To learn more about it, log into the `enb1` node. The eNodeB
service is attached to a `screen` and also clones its output to a log
in `/var/log/oai/enb.log`.

To view the live output via screen, run:

    sudo screen -r enb

To detach from the screen without stopping the program, type `Ctrl-a d`.
You can find out more about using screen with `man screen`.

Since the eNodeB is development software that is still under
production, there are still a lot of cases where it might abort on an
error instead of handling it gracefully. If this happens, the screen
will go away, but the log file persists so you can investigate the
cause. And you can restart the service by hand with:

    sudo /lcoal/repository/bin/enb.start.sh

## Inspecting the EPC

The EPC works in much the same way as the eNodeB. The MME, HSS, and
SPGW services all run on the `epc` node. These services log to:

    /var/log/oai/mme.log
    /var/log/oai/hss.log
    /var/log/oai/spgw.log

And they all have screen sessions as well that can be found at:

    sudo screen -r mme
    sudo screen -r hss
    sudo screen -r spgw

In particular, by default the MME logs a status message every few
seconds which indicates if there is a connected eNodeB, attached UE,
or connected UE.

## Debugging the system

As a system under development, OAI is not always stable.

It is likely that there will be errors that crop up either on the RAN
side or at the EPC. When an error happens on the RAN side, the eNodeB
will flag it to its log file and send a `UE Context Release` message
to the MME.

In the current version, the MME will often respond by setting the UE
to an idle state from which it never comes up. You can see this by
looking at the MME logs and seeing that it lists the UE as attached
but not connected.

If you see this happen, rebooting the associated nodes or restarting
the services should allow the UE to reconnect.

## Capturing Traffic

The control traffic for OAI can be captured with tcpdump on the proper
interfaces. For example, if you log into the `enb1` node, you can look
at the configuration file for the enb service at
`/usr/local/etc/oai/enb.conf`. There, you will find that the
`mme_ip_address` is likely set to something like `10.10.4.2`. Then by
running `ifconfig`, you can find the vlan interface on that same
subnet. And now you can run something like:

    sudo tcpdump -i vlan123

This will let you see the traffic as it flows or you can redirect the
output to a file and run wireshark or other analysis software on it.

## HSS Database

The HSS has a database which is used as a persistent store for things
like valid IMSI values for UEs. This database is pre-populated with
the IMSI of your UE when the experiment begins.

Look in `/usr/local/etc/oai/hss.conf` to see the database
parameters. You can then log into the database to see or change the
persistent state of the HSS:

    mysql --user=root --password=linux oai_db
