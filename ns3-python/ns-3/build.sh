repo="$PWD"
base="$repo/ns-3"

section ---------------- install ----------------
run apt-get update
run apt-get install -y --no-install-recommends \
	bzip2 \
	cmake \
	curl \
	g++ \
	git \
	libclang-dev \
	llvm-dev \
	make \
	patch \
	patchelf \
	python3-dev \
	python3-pip \
	python3-setuptools \
	python3-wheel \
	qt5-default \
	zip \
	&& true

export NS3_VERSION=3.33

# 3.33
ns3_download_sha1=d20b5ca146975f202655c1940db57f53c9f574a1

section ---------------- download ----------------
workdir /opt/ns-3
run curl -L -o ../ns-3.tar.bz2 https://www.nsnam.org/releases/ns-allinone-$NS3_VERSION.tar.bz2
runsh "echo '${ns3_download_sha1} ../ns-3.tar.bz2' | sha1sum -c"
run tar xj --strip-components 1 -f ../ns-3.tar.bz2


section ---------------- NetAnim ----------------
workdir netanim-*
run qmake NetAnim.pro
run make -j $(nproc)

section ---------------- ns-3 ----------------
workdir "/opt/ns-3/ns-$NS3_VERSION"
run ./waf configure

workdir "/opt/ns-3"
run ./build.py -- install --destdir=/ns-3-build
run cp netanim-*/NetAnim /ns-3-build/usr/local/bin

section ---------------- python wheel ----------------
run cp "$base/__init__.py" /ns-3-build/usr/local/lib/python3.9/site-packages/ns/

run cp -r "$base/ns" /opt/ns

workdir /opt/ns
run python3 setup.py bdist_wheel
run python3 -m wheel unpack -d patch "dist/ns-$NS3_VERSION-py3-none-any.whl"

ns3_patch="patch/ns-$NS3_VERSION"

run rm -r "$ns3_patch/ns/_/lib/python3"

for f in "$ns3_patch"/ns/*.so; do
	run patchelf --set-rpath '$ORIGIN/_/lib' "$f";
done

for f in "$ns3_patch"/ns/_/bin/*; do
	run patchelf --set-rpath '$ORIGIN/../lib' "$f";
	run chmod +x "$f";
done

for f in "$ns3_patch"/ns/_/lib/*.so; do
	run patchelf --set-rpath '$ORIGIN' "$f";
done

run mkdir dist2
run python3 -m wheel pack -d dist2 "$ns3_patch"
