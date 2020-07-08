STATIC_RESOURCES := Contents/Info.plist icon.png icon@2x.png
.SECONDARY:

#
# Publishing
#

.build/%/AWS-CLI-v2.tgz: .build/%/AWS-CLI-v2.docset/.done
	cd "$(dir $@)" && \
		tar --exclude='.DS_Store' -czf AWS-CLI-v2.tgz AWS-CLI-v2.docset

#
# Docset
#

.build/%/AWS-CLI-v2.docset/.done: \
		.build/%/AWS-CLI-v2.docset/Contents/Resources/Documents \
		.build/%/AWS-CLI-v2.docset/Contents/Resources/docSet.dsidx \
		$(addprefix .build/%/AWS-CLI-v2.docset/,$(STATIC_RESOURCES))
	touch "$@"

.build/%/AWS-CLI-v2.docset/Contents/Resources/Documents: \
		.build/%/aws-cli/doc/build/html \
		.build/%/.venv
	mkdir -p "$(dir $@)"
	set -e && \
		tmp="$$(mktemp -d)" && \
		cp -r "$<" "$$tmp" && \
		source ".build/$*/.venv/bin/activate" && \
		./scripts/transform.py "$$tmp/html" && \
		mv "$$tmp/html" "$@"

.build/%/AWS-CLI-v2.docset/Contents/Resources/docSet.dsidx: \
		.build/%/aws-cli/doc/build/html \
		.build/%/.venv
	mkdir -p "$(dir $@)"
	set -e && \
		source ".build/$*/.venv/bin/activate" && \
		./scripts/index.py ".build/$*/aws-cli/doc/build/html" "$@"

.build/%/AWS-CLI-v2.docset/Contents/Info.plist: static/Info.plist
	mkdir -p "$(dir $@)"
	cp "static/$(notdir $@)" "$@"

.build/%/AWS-CLI-v2.docset/icon.png: static/icon.png
	mkdir -p "$(dir $@)"
	cp "static/$(notdir $@)" "$@"

.build/%/AWS-CLI-v2.docset/icon@2x.png: static/icon@2x.png
	mkdir -p "$(dir $@)"
	cp "static/$(notdir $@)" "$@"

.build/%/.venv:
	python3 -m venv "$@" && \
		source "$@/bin/activate" && \
		pip install -r requirements.txt

#
# AWS CLI v2 documentation
#

.build/%/aws-cli/doc/build/html: .build/%/aws-cli
	cd ".build/$*/aws-cli" && \
		python3 -m venv .venv && \
		source .venv/bin/activate && \
		pip install -r requirements.txt -r requirements-docs.txt && \
		python setup.py install && \
		cd doc && \
		make html

.build/%/aws-cli:
	git clone \
		--depth 1 \
		--branch "$*" \
		https://github.com/aws/aws-cli.git \
		$@
