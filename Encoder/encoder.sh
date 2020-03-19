#!/bin/bash
# --- 80 Columns ------------------------------------------------------------- #
# Description:
# Author: Jack~D

DIRECTORY=$(cd $(dirname ${0}) && pwd) # This directory
INPUT='' # Path to input video file
OUTPUT='' # Path to output directory
DEBUG=false
QUIET=false
YES=false
RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
WHITE=$(tput sgr0)

helpText() {
   echo -e ' -d --debug\tDebug mode'
   echo -e ' -h --help\tHelp information'
   echo -e ' -i --input\tPath to input video file'
   echo -e ' -o --output\tPath to output directory'
   echo -e ' -q --quiet\tSilence printing output'
   echo -e ' -y --yes\tForce yes to questions'
}

# Strip surrounding whitespace
strip() {
   echo $(<'/dev/stdin') | sed 's/^\s*\|\s*$//g'
}

handleParameters() {
   let 'COUNT = 0'
   while [ "$1" != '' ]
   do
      PARAM=$(echo $1 | awk -F= '{print $1}')
      VALUE=$(echo $1 | awk -F= '{print $2}')
      case $PARAM in
         -d | --debug )
            DEBUG=true
            ;;
         -h | --help | 'help')
            helpText # Print help text
            exit '0'
            ;;
         -i | --input)
            INPUT=$(echo $VALUE | strip)
            ;;
         -o | --output)
            OUTPUT=$(echo $VALUE | strip)
            ;;
         -q | --quiet )
            QUIET=true
            ;;
         -y | --yes )
            YES=true
            ;;
         *)
            VALUE="${PARAM}"
            if [ "${COUNT}" = '0' ]
            then
               INPUT=$(echo "${VALUE}" | strip)
            elif [ "${COUNT}" = '1' ]
            then
               OUTPUT=$(echo "${VALUE}" | strip)
            else
               echo -e "\a[ ${RED}ERROR${WHITE} ] Too many arguments."
               exit '1'
            fi
            let 'COUNT++'
            ;;
      esac
      shift
   done
   if [ "${INPUT}" = '' ]
   then
      echo -e -n "\a[ ${RED}ERROR${WHITE} ] No input file. Call with --help "
      echo 'for more information.'
      exit '1'
   fi
   if [ ! -f "${INPUT}" ]
   then
      echo -e -n "\a[ ${RED}ERROR${WHITE} ] Input video file \"${INPUT}\" was "
      echo 'not found.'
      exit '1'
   fi
   if [ "${OUTPUT}" = '' ]
   then
      OUTPUT=$(echo ${INPUT%.*} | strip)
   fi
   if [ "${OUTPUT}" = '' ]
   then
      echo -e -n "\a[ ${RED}ERROR${WHITE} ] Something is wrong with output "
      echo -e 'directory.'
      exit 1
   fi
   if [ -d "${OUTPUT}" ]
   then
      if [ "$(ls ${OUTPUT} | strip)" != '' ]
      then
         echo -e "\a[ ${YELLOW}WARNING${WHITE} ] Output directory is not empty."
         exit 1
      fi
   else
      mkdir -p "${OUTPUT}" || exit '1'
   fi
   if [ ${DEBUG} = true -a ${QUIET} = false ]
   then
      echo -e "Input = \"${INPUT}\"\nOutput = \"${OUTPUT}\""
   fi
}

main()
{
   handleParameters "${@}"
}

main "${@}"

# END OF LINE