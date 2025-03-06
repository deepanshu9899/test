#!/bin/sh
HERE=`dirname $0`
MODULE_HOME=`cd $HERE/..; pwd`
cd $MODULE_HOME

propertiesFile="config/user.properties"
wrapperConf="config/wrapper.conf"
jreSecurity="jre/lib/security/"

cleanFlagFromPropertiesFile() {
  regex="^[ ]*$1[ ]*=[ ]*"
  if [ -f ${propertiesFile} ]; then
    if grep -qE "${regex}" ${propertiesFile}; then
      sed -i'.original' -e "/${regex}/d" ${propertiesFile}
    fi
  fi
}

setFipsJceInUserProperties() {
  cleanFlagFromPropertiesFile "fipsJce"
  echo "fipsJce=true" >> ${propertiesFile}
}

setOptionalLibClasspathToBcFipsJar() {
  sed -i'.original' -e 's:optional-lib/bcp\*:optional-lib/bc-fips-\*:' ${wrapperConf}
}

showUsage() {
  echo "Usage: $0 [ -h ] [ -j JAVA_HOME_PATH ]"
}

case $1 in
  disable)
    cleanFlagFromPropertiesFile "fipsJce"
    sed -i'.original' -e 's:optional-lib/bc-fips-\*:optional-lib/bcp\*:' ${wrapperConf}
    ;;

  *)
    while getopts ":hj:" option; do
      case "${option}" in
        h)
          showUsage
          echo "h : print this help message"
          echo "j : pass the absolute path of the java home directory"
          exit 0
          ;;

        j)
          setFipsJceInUserProperties
          setOptionalLibClasspathToBcFipsJar
          cleanFlagFromPropertiesFile "wrapper.java.command"
          echo "wrapper.java.command=${OPTARG}/bin/java" >> ${propertiesFile}
          cp certs/bcfkscacerts ${OPTARG}/lib/security/
          exit 0
          ;;

        :)
          echo "Error: -${OPTARG} requires an argument."
          showUsage
          exit 1
          ;;

        *)
          echo "Illegal option: -${OPTARG}"
          exit 1
          ;;
      esac
    done

    # Default code to be executed when no options are passed
    # Copy bckfs cert to jre/lib/security
    javaPath=`cat ${propertiesFile} | grep "wrapper.java.command" | cut -d'=' -f2 | awk '{$1=$1};1'`
    if [ -n "${javaPath}" ]; then
      javaBinDir=`dirname ${javaPath}`
      javaHomeDir=`cd ${javaBinDir}/..; pwd`
      javaSecurityDir=${javaHomeDir}/lib/security/
      if [ -d ${javaSecurityDir} ]; then
        cp certs/bcfkscacerts ${javaSecurityDir}
      else
        echo "Trouble finding the Java Home path. Please re-run the script with -j option"
        exit 1
      fi
    elif [ -d ${jreSecurity} ]; then # Only for RPM / DEB as no JRE is shipped with TAR
      cp certs/bcfkscacerts ${jreSecurity}
    elif [ -n "${JAVA_HOME}" ]; then
      cp certs/bcfkscacerts ${JAVA_HOME}/lib/security/
    else
      echo "JRE not found. Please re-run the script with -j option"
      exit 1
    fi

    setFipsJceInUserProperties
    setOptionalLibClasspathToBcFipsJar
    ;;
esac
