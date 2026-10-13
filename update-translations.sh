#!/bin/bash

langs=("tr" "pt")

if ! command -v xgettext &> /dev/null
then
	echo "xgettext could not be found."
	echo "you can install the package with 'apt install gettext' or 'pacman -S gettext'."
	exit 1
fi

echo "updating pot file"
xgettext -o po/parslinux-package-installer.pot --files-from=po/files --from-code=UTF-8

for lang in ${langs[@]}; do
	if [[ -f po/$lang.po ]]; then
		echo "updating $lang.po"
		msgmerge -o po/$lang.po po/$lang.po po/parslinux-package-installer.pot
	else
		echo "creating $lang.po"
		cp po/parslinux-package-installer.pot po/$lang.po
	fi
done