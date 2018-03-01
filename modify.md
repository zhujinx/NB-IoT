# Modifying Your Experiment

This profile is meant to be a jumping-off point for creating your own
experiments. As such, you have access to the source code for OAI
itself, the ability to modify and recompile it, and you can even
create your own profiles by cloning this repository.

## Source Code

The source code for OAI is located in `/opt/oai` on both the `enb1`
and `epc` nodes. This source code is a snapshot of the [official
repositories](https://gitlab.eurecom.fr/oai).

The `/opt/oai` directory is a mounted blockstore which acts as a local
clone. It is both readable and writeable, but the changes you make
won't persist when your experiment is gone.

### Before Building

When building, installation will fail if the associated service is
still running. In addition, OAI is still a work in progress and is
therefore somewhat fragile when the services don't start up in the
right order. For these reasons, it is usually best to kill all
services before building from source and then restart them in the
correct order afterwards.

Run this on the `enb1` node:

   sudo /local/repository/bin/enb.kill.sh

Run this on the `epc` node:

   sudo /local/repository/bin/mme.kill.sh
   sudo /local/repository/bin/hss.kill.sh
   sudo /local/repository/bin/spgw.kill.sh

After these steps, rebuild whichever services you have modified as described below.

### Building the eNodeB

The official repository for the eNodeB source code is
[here](https://gitlab.eurecom.fr/oai/openairinterface5g) along with
[build
documentation](https://gitlab.eurecom.fr/oai/openairinterface5g). A
snapshot of that repository can be found on the `enb1` node in your
experiment located at `/opt/oai/openairinterface5g`.

You can see exactly which commit this blockstore was forked from:

   cd /opt/oai/openairinterface5g
   git log

Aside from a minor patch which slimmed down the build dependencies,
this is a snapshot of the development branch of the repository.

If you would like to rebuild the source after making some
modification, first kill the enodeb service:

   cd /opt/oai/openairinterface5g/cmake_targets
   sudo ./build_oai --eNB -w USRP

### Building the MME, HSS, or SPGW

The core network services have a separate
[repository](https://gitlab.eurecom.fr/oai/openair-cn) and are built
using a slightly different
[procedure](https://gitlab.eurecom.fr/oai/openairinterface5g/wikis/AutoBuild#building-the-epc-modules-newer-version-latest-developmaster-branch). The
snapshot for this repository is located on the `epc` node in your
experiment in the `/opt/oai/openair-cn` directory.

To build the MME from source:

   cd /opt/oai/openair-cn/SCRIPTS
   sudo ./build_mme

To build the HSS from source:

   cd /opt/oai/openair-cn/SCRIPTS
   sudo ./build_hss

To build the SPGW from source:
   cd /opt/oai/openair-cn/SCRIPTS
   sudo ./build_spgw


### Restarting After Rebuilding

You can re-run the startup script on both `enb1` and `epc` nodes. This
will start all services again and syncronize their startups to ensure
the start in the proper order.

On the `epc` node:

   sudo /local/repository/bin/config_oai.pl -r EPC

On the `enb` node:

   sudo /local/repository/bin/config_oai.pl -r ENB

### Saving Source Code Changes Permanently

In order to save changes permanently, you will need an external git
repository. Then add it as a remote in `/opt/oai/openair-cn` or
`/opt/oai/openairinterface5g` and push up your changes.

   cd /opt/oai/openair-cn
   git remote add myrepo url-or-ssh-path-to-my-repo
   git push myrepo

Then on later experiments you can add your experiment as a remote,
pull, and rebuild.

## Modifying This Profile

This profile is itself in a git repository. Whenever an experiment is
instantiated, that repository is cloned to `/local/repository`. You
can make your own clone of the repository, modify either the resource
allocation geni-lib script or any of the startup or utility scripts,
and create a new profile based on your cloned repository.

### Resource Allocation

The resource allocation script is in `/local/repository/profile.py`
and this Python script is run before the experiment begins to specify the
resources that will be used for the experiment. You could modify it to
add other compute nodes, other radios, or change what scripts are run
at startup.

The geni-lib libraries that are used to build up this resource
specification are described in our
[documentation](http://docs.powderwireless.net/geni-lib.html). Modifying
`profile.py` after an experiment begins won't change the allocated
resources of that experiment.

### Startup Scripts

In `profile.py`, a startup script is specified for the `enb1` and
`epc` nodes. That script is located in
`/local/repository/bin/config_oai.pl`. This script is executed (with
`/the parameters specified in `profile.py`) at experiment startup and
`/every time the experiment boots.

The first time `config_oai.pl` runs, it uses the configuration
templates in `/local/repository/etc/*` to generate configuration files
for all of the OAI services. Then it touches
`/var/emulab/boot/OAI_CONFIG_DONE` so that it won't regenerate those
files on future run-throughs. If you want to regenerate the
configuration files on `enb1` or `epc`, remove
`/var/emulab/boot/OAI_CONFIG_DONE` and rerun `config_oai.pl`.

After generating the configuration files, `config_oai.pl` starts up
all the services in a synchronized way. The instance running on the
`epc` node starts up the MME, HSS, and SPGW and then waits. And the
instance running on the `enb1` node waits until all the other services
are started before beginning the eNodeB. If one is run without the
other, it will wait forever. The `config_oai.pl` script logs its
output to `/var/log/oai/startup.log` in addition to printing it to
standard out.

### Service Scripts

The other scripts in `/local/repository/bin` provide a way to manage
each individual service by hand. They can start or stop any of the OAI
services. There is no synchronization here. Each one of them sets up a
screen session, and also clones their output to log files into a file
in `/var/log/oai`.

### Creating a Profile

While any of these scripts can be modified, the changes won't persist
unless you create your own profile. Go to the portal, select this
profile, and click 'copy'.

A pop-up box will tell you the URL of this repository and you will
need to use that URL to fork this repository using gitlab or github or
some other git hosting service.

Once you have forked the repository, you can paste the URL for the new
repository and then your new profile will point at your new
repository. In order to have the new profile automatically track
changes to the forked repository, you will need to set up a push hook
on the fork.

[Full Documentation on Repository-Based Profiles](http://docs.powderwireless.net/creating-profiles.html#%28part._repo-based-profiles%29)

