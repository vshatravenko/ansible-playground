TAG = debian-stable-slim
IMAGE = valshatravenko/ansible-target:$(TAG)
TARGET_USER = ansible
BUILD_ARCH 	?= $(shell uname -m)
PRIV_KEY ?= id_lol
PUB_KEY_B64 ?= $(shell cat $(PRIV_KEY).pub | base64 -w0)
OUT_DIR ?= output
SSH_PRIV_KEY ?= $(OUT_DIR)/id_ap
SSH_PUB_KEY ?= $(SSH_PRIV_KEY).pub

.PHONY: build
build:
	docker build --build-arg TARGET_USER=$(TARGET_USER) \
		--platform linux/$(BUILD_ARCH) \
		-t $(IMAGE) .

.PHONY: push
push: build
	docker push --platform linux/${BUILD_ARCH} $(IMAGE)

.PHONY: run-local
run-local: ssh-key
	docker rm -f sshd
	docker run -e SSH_PUB_KEY_B64=$(PUB_KEY_B64) \
		--platform linux/$(BUILD_ARCH) \
		--name sshd \
		-d $(IMAGE)

.PHONY: render
render: ssh-key
	@./bin/render.py

.PHONY: compose-up
compose-up:
	@docker compose up -Vd

.PHONY: compose-down
compose-down:
	@docker compose down -t 1

.PHONY: compose-erase
compose-erase:
	@docker compose down -t 1 -v

$(SSH_PRIV_KEY):
	mkdir -p $(OUT_DIR)
	ssh-keygen -N '' -f $(SSH_PRIV_KEY)
	chmod 0600 $(SSH_PRIV_KEY)

.PHONY: ssh-key
ssh-key: $(SSH_PRIV_KEY)

.PHONY: ssh-local
ssh-local:
	$(eval SSHD_IP = $(shell docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' sshd))
	ssh -i $(PRIV_KEY) $(TARGET_USER)@$(SSHD_IP)
