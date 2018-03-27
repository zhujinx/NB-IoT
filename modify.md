# Modifying Your OAI Build

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
documentation](https://gitlab.eurecom.fr/oai/openairinterface5g/wikis/AutoBuild#install-build-enb). A
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

You can re-run the startup script on either `enb1` or `epc` nodes. This
will start all services again and syncronize their startups to ensure
the start in the proper order.

On the `epc` node:

    sudo /local/repository/bin/start_oai.pl

### Saving Source Code Changes Permanently

In order to save changes permanently, you will need an external git
repository. Then add it as a remote in `/opt/oai/openair-cn` or
`/opt/oai/openairinterface5g` and push up your changes.

    cd /opt/oai/openair-cn
    git remote add myrepo url-or-ssh-path-to-my-repo
    git push myrepo

Then on later experiments you can add your experiment as a remote,
pull, and rebuild.
