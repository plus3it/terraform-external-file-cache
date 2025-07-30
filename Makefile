SHELL := /bin/bash

ifneq ($(findstring --nomock,$(PYTEST_ARGS)),--nomock)
# Set "s3_endpoint_url" only if PYTEST_ARGS *does not* contain "--nomock"
# In the mockstack container, MOCKSTACK_HOST is set and will be the correct endpoint
# Outside the mockstack container, "localhost" should be the correct endpoint
MOCKSTACK_LOCAL = $(or $(MOCKSTACK_HOST),localhost)
terraform/pytest: export TF_VAR_s3_endpoint_url = http://$(MOCKSTACK_LOCAL):4615
endif

include $(shell test -f .tardigrade-ci || curl -sSL -o .tardigrade-ci "https://raw.githubusercontent.com/plus3it/tardigrade-ci/master/bootstrap/Makefile.bootstrap"; echo .tardigrade-ci)
