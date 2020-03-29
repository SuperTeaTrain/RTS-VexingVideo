#!/bin/sh
# --- 80 Columns ------------------------------------------------------------- #
# Description:
# Author: Jack~D

DIRECTORY=$(cd $(dirname ${0}) && pwd) # Path to this directory
INPUT='' # Path to input video file
OUTPUT='' # Path to output directory
FPS=''

# Flags
DEBUG=false # Debug mode
QUIET=false # Silence printing output
YES=false # Force yes to questions

# Colors
RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
WHITE=$(tput sgr0)

# Print help information
helpText() {
   echo -e ' -d --debug\tDebug mode'
   echo -e ' -f --fps\tOutput frames per second'
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
   while [ "${1}" != '' ]
   do
      PARAM=$(echo ${1} | awk -F= '{print $1}')
      VALUE=$(echo ${1} | awk -F= '{print $2}')
      case "${PARAM}" in
         -d | --debug )
            DEBUG=true
            ;;
         -f | --fps )
            FPS=$(echo ${VALUE} | strip)
            ;;
         -h | --help | 'help' | 'Help' | 'HELP' )
            helpText # Print help information
            exit '0'
            ;;
         -i | --input )
            INPUT=$(echo ${VALUE} | strip)
            ;;
         -o | --output )
            OUTPUT=$(echo ${VALUE} | strip)
            ;;
         -q | --quiet )
            QUIET=true
            ;;
         -y | --yes )
            YES=true
            ;;
         *)
            VALUE="${PARAM}"
            [ "${COUNT}" = '0' ] && INPUT=$(echo "${VALUE}" | strip)
            [ "${COUNT}" = '1' ] && OUTPUT=$(echo "${VALUE}" | strip)
            if [ "${COUNT}" -gt '1' ]
            then
               echo -e "\a[ ${RED}ERROR${WHITE} ] Too many arguments."
               exit '1'
            fi
            let 'COUNT++'
            ;;
      esac # End case
      shift
   done # End while
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
   [ "${OUTPUT}" = '' ] && OUTPUT=$(echo ${INPUT%.*} | strip)
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
         echo -e "\a[ ${RED}ERROR${WHITE} ] Output directory is not empty."
         exit 1
      fi
   else
      if [ ${QUIET} = false -a ${YES} = false ]
      then
         echo -e "\a[ ${YELLOW}WARNING${WHITE} ] Output directory is not found."
         echo -n 'Automatically create an output directory (y/n)? '
         read ANSWER
         if [ "${ANSWER}" = "${ANSWER#[Yy]}" ]
         then
            exit '0'
         fi
      fi
      if [ ${DEBUG} = true -a ${QUIET} = false ]
      then
         echo -e "Making directory \"${OUTPUT}\""
      fi
      mkdir -p "${OUTPUT}" || exit '1'
   fi
   mkdir -p "${OUTPUT}/I-Frames" || exit '1'
   mkdir -p "${OUTPUT}/P-Frames" || exit '1'
   mkdir -p "${OUTPUT}/Frames" || exit '1'
   mkdir -p "${OUTPUT}/Audio" || exit '1'
   if [ ${DEBUG} = true -a ${QUIET} = false ]
   then
      echo -e "Input = \"${INPUT}\"\nOutput = \"${OUTPUT}\""
      echo "FPS = \"${FPS}\""
   fi
}

dependencies() {
   if [ "$(which ffmpeg | strip)" != '' ]
   then
      [ ${QUIET} = false ] && echo -e "\a[ ${GREEN}OK${WHITE} ] ffmpeg"
   else
      echo -e -n "\a[ ${RED}ERROR${WHITE} ] ffmpeg not in PATH. Please install "
      echo 'ffmpeg and add to PATH.'
      exit '1'
   fi
   if [ "$(which ffmpeg | strip)" != '' ]
   then
      [ ${QUIET} = false ] && echo -e "\a[ ${GREEN}OK${WHITE} ] convert"
   else
      echo -e -n "\a[ ${RED}ERROR${WHITE} ] convert not in PATH. Please install"
      echo ' imagemagick and add to PATH.'
      exit '1'
   fi
}

main()
{
   handleParameters "${@}"
   dependencies "${@}"
   
   # ffmpeg command
   # Extracts frame images
   PARAMS="'${INPUT}' '${OUTPUT}/I-Frames/%10di.png'"
   [ "${QUIET}" = true ] && PARAMS=$(echo -n "${PARAMS} -loglevel 'fatal'")
   [ "${FPS}" != '' ] && PARAMS=$(echo -n "${PARAMS} -vf fps='${FPS}'")
   [ "${DEBUG}" = true -a "${QUIET}" = false ] &&  echo "PARAMS = \"${PARAMS}\""
   echo -n "xargs ffmpeg -i ${PARAMS}"  | sh || exit '1'
   
   cp "${OUTPUT}/I-Frames/0000000001i.png" "${OUTPUT}/P-Frames/0000000001p.png"
   cp "${OUTPUT}/I-Frames/0000000001i.png" "${OUTPUT}/Frames"
   END=$(ls "${OUTPUT}/I-Frames" -1 | wc -l | strip)
   
   for i in $(seq 1 ${END})
   do
      echo ${i}
      if [ "$(expr ${i} % 60 | strip)" = '0' ]
      then
          echo 'Yes'
          FILE=$(printf "${OUTPUT}/I-Frames/%010di.png" ${i})
          cp "${FILE}" "${OUTPUT}/Frames"
      fi
   done
   
   END=$(expr ${END} - 1)
   for i in $(seq 2 ${END})
   do
      if [ "${DEBUG}" = true -a "${QUIET}" = false ]
      then
         printf "Frame %010d\n" "${i}"
      fi
      
      # imagemagic command
      # "-median" reduces images clarity for smaller file size
      convert \
      '(' $(printf "${OUTPUT}/I-Frames/%010di.png" $(expr "${i}" + 1)) \
      -median 5 ')' \
      '(' $(printf "${OUTPUT}/I-Frames/%010di.png" ${i}) -median 5 ')' \
      '(' -clone 0 -clone 1 -compose difference -composite -threshold 5000 ')' \
      -delete 1 -alpha off -compose copy_opacity -composite \
      $(printf "${OUTPUT}/P-Frames/%010dp.png" ${i}) || exit '1'
      
   done # End for loop
   
   NUM=$(ls "${OUTPUT}/P-Frames" -1 | wc -l | strip)
   NUM=$(echo "${NUM} * 0.05" | bc | awk '{print int($1+2)}' | strip)
   for i in $(ls --sort=size -l "${OUTPUT}/P-Frames" \
      | sed "${NUM}q" | awk '{print $9}' | awk '/./' | sed 's/p\./i\./g')
   do
      cp "${OUTPUT}/I-Frames/${i}" "${OUTPUT}/Frames"
   done
}

main "${@}"

# END OF LINE

