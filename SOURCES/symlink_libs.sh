#!/bin/bash

# This script replaces plugins with symlinks
# $1 : folder to replace with symlinks

set -e

SCL_JAVA_DIRS=${@:2}

pushd () {
	command pushd "$@" > /dev/null
}

popd () {
	command popd "$@" > /dev/null
}

function _sym {
	if [ -f $1 ]; then
		echo "linking $1 to $2"
		rm -rf $1
		ln -s $2 $1
	else
		echo "Failed to find $1"
		ls -l
		exit 1
	fi
}

function _symlink {
	_f=$(ls | grep -e "^$1" || :)
	if [ -n "$_f" ] ; then
		rm -rf $_f
		for SCL_JAVA_DIR in ${SCL_JAVA_DIRS}; do
			if [ -f ${SCL_JAVA_DIR}/$2  ]; then
				echo "linking ${_f%.jar}.jar to ${SCL_JAVA_DIR}/$2"
				ln -s ${SCL_JAVA_DIR}/$2 ${_f%.jar}.jar
				return 0
			fi
		done
		echo "not found $2 in any of ${SCL_JAVA_DIRS}"
		exit 1
	fi
}

pushd $1
	# owasp-java-encoder
	_sym org.owasp.encoder_1.2.2.jar /usr/share/java/owasp-java-encoder/encoder.jar
	# jakarta-activation
	_sym com.sun.activation.jakarta.activation_1.2.2.jar /usr/share/java/jakarta-activation/jakarta.activation.jar
	# HdrHistogram
	_sym org.hdrhistogram.HdrHistogram_2.1.11.jar /usr/share/java/HdrHistogram.jar
	# javamail
	_sym com.sun.mail.jakarta.mail_1.6.5.jar /usr/share/java/jakarta-mail/jakarta.mail.jar
	# jmc-core
	_symlink org.openjdk.jmc.common_ common.jar
	_symlink org.openjdk.jmc.flightrecorder_ flightrecorder.jar
	_symlink org.openjdk.jmc.flightrecorder.rules_ flightrecorder.rules.jar
	_symlink org.openjdk.jmc.flightrecorder.rules.jdk_ flightrecorder.rules.jdk.jar
popd
