#!/bin/bash

PROG=$(basename "$0")
usage() {
    echo "
    usage: $PROG [Options]
      Example: ./$PROG -r devopsadmin
      This application automates the conversion of HG repos to Git
      -h      : display this help
      -r 	  : Name of the main repo
    "
}

while getopts ":r:h" opt; do
    let optnum++
    case $opt in
        r ) mainRepo+=${OPTARG};;
        h ) usage=${OPTARG};;
        \?) usage; exit 1;;
        : ) echo -e "${yellow}Missing repo name!"; exit 1;;
    esac
done


#variables
workspaceDir=~/workspace/
mainRepoName=${mainRepo,,}
AUTH='Authorization: Basic YOURKEY'
HgUrl="ssh://hg@bitbucket.org/YOURORGANIZATION/"
GitURL="git@bitbucket.org:YOURORGANIZATION"
APIURL="https://api.bitbucket.org/2.0/repositories/YOURORGANIZATION"
fastExportDir="${workspaceDir}/fast-export"
mainHgURL=${HgUrl}${mainRepoName}
mainGitRepoName="${mainRepoName}-git"
mainHGDir=${workspaceDir}${mainRepoName}
mainGitDir=${workspaceDir}${mainGitRepoName}
subs=false
#create workspace directory
if ! [[ -d ${workspaceDir} ]]; then
    mkdir ${workspaceDir}
fi
#clone frej's fast-export
if ! [[ -d ${fastExportDir} ]]; then
    cd ${workspaceDir}
    git clone https://github.com/frej/fast-export.git
fi 

cd ${workspaceDir}
#make main git directory
if ! [[ -d ${mainGitDir} ]]; then
    mkdir ${mainGitDir}
fi
#make main HG directory
if ! [[ -d ${mainHGDir} ]]; then
    hg clone ${mainHgURL}
fi
#check if the repo has any submodules
cd ${mainHGDir}
if [[ -f .hgsub ]]; then
    subs=true
fi

##################################################################################################################
#                                                    SUBREPOS                                                    #
##################################################################################################################

function doSubRepos {
    cd ${mainHGDir}
    fileName=".hgsub"
    repoList=`cat ${fileName}`
    IFS=$'\n' 
    for subrepo in ${repoList}; do
        subRepoPath=$(echo ${subrepo} | awk '{print $1}')
        subRepoName=$(echo ${subrepo} | sed "s:.*/::" | tr -d '\r')
        subProjectKeyName=`curl -s -X GET -H "${AUTH}" -H "Content-Type: application/json" "${APIURL}/${subRepoName}" | jq -r '.project.key'`
        subGitName="${subRepoName}-git"
        subGitSCM=`curl -s -X GET -H "${AUTH}" -H "Content-Type: application/json" "${APIURL}/${subGitName}" | jq -r '.'`
        if ! [[ ${subGitSCM} = *"error:"* ]]; then
            echo "There is already a Git version of ${subRepoName}. Skipping..."
            continue
        fi
        tags=false
        cd ${workspaceDir}
        #clone the repo
        subHgURL=${HgUrl}${subRepoName}
        if ! [[ -d ${subRepoName} ]]; then
            hg clone ${subHgURL}
        fi
        #do the tags
        cd ${subRepoName}
        if [[ -f .hgtags ]]; then 
            tags=true
            tr A-Z a-z < .hgtags >> toLower
            sed 's/ /"="/' toLower > EqualsQuotes
            rm toLower
            sed 's/ /-/g' EqualsQuotes > RemovedSpaces
            rm EqualsQuotes
            awk '{ print "\""$0"\""}' RemovedSpaces > ${workspaceDir}/tags.map
            rm RemovedSpaces
        fi
        #Then convert the subrepo
        cd ${workspaceDir}
        if ! [[ -d ${subGitName} ]]; then
            mkdir ${subGitName}
        fi
        cd ${subGitName}
        git init
        if ${tags}; then
            ${fastExportDir}/hg-fast-export.sh -r ${workspaceDir}${subRepoName} -T ${workspaceDir}/tags.map --hgtags
        else
            ${fastExportDir}/hg-fast-export.sh -r ${workspaceDir}${subRepoName}
        fi
        if [ $? -ne 0 ]; then
        	echo -e "The Fast Export command did not run properly!"
        	exit 1
        fi
        ##Do the git stuff
        git checkout HEAD
        #convert the .hgignore to .gitignore
        if [[ -f .hgignore ]]; then
            mv .hgignore .gitignore
            sed -i '/# use glob syntax./d' ./.gitignore
            sed -i '/syntax: glob/d' ./.gitignore
        fi
        #remove all the .hg files
        rm -rf .hg*
        git add .
        git commit -m "Converted ${subRepoName} from HG to Git. First upload."
        #Add the local stuff to remote
        subGitSCM=`curl -s -X GET -H "${AUTH}" -H "Content-Type: application/json" "${APIURL}/${subGitName}" | jq -r '.'`
        if [[ ${subGitSCM} = *"error"* ]]; then
            #Create the main repo in BitBucket
            curl -s -X POST -H "${AUTH}" -H "Content-Type: application/json" -d '{
                "scm": "git",
                "project": {
                    "key": "'${subProjectKeyName}'"
                },
                "fork_policy": "no_public_forks",
                "is_private": "true"
            }'${APIURL}/${subGitName}
            git remote add origin ${GitURL}/${subGitName}.git
            git push -u origin master
            if ${tags}; then
                git push --all
                git push --tags
            else
                git push --all
            fi
            #Create .gitmodules file
            cd ${workspaceDir}
            cat <<EOF >> submodule-mappings
"${subRepoPath}"="../${subGitName}"
EOF
        else
            echo "${subGitName} exists. Going to next..."
        fi
   done
}

##################################################################################################################
#                                                    MAIN REPO                                                   #
##################################################################################################################
function mainRepo {

    projectKeyName=`curl -s -X GET -H "${AUTH}" -H "Content-Type: application/json" "${APIURL}/${mainRepoName}" | jq -r '.project.key'`  
    #do the tags
    tags=false
    cd ${mainHGDir}
    if [[ -f .hgtags ]]; then 
        tags=true
        tr A-Z a-z < .hgtags >> toLower
        sed 's/ /"="/' toLower > EqualsQuotes
        rm toLower
        sed 's/ /-/g' EqualsQuotes > RemovedSpaces
        rm EqualsQuotes
        awk '{ print "\""$0"\""}' RemovedSpaces > ${workspaceDir}/tags.map
        rm RemovedSpaces
    fi
    #Then convert the main repo
    cd ${mainGitDir}
    git init
    if ${tags} && ${subs}; then
        ${fastExportDir}/hg-fast-export.sh -r ${mainHGDir} -T ${workspaceDir}/tags.map  --hgtags --subrepo-map=${workspaceDir}/submodule-mappings
    elif ${subs}; then
        ${fastExportDir}/hg-fast-export.sh -r ${mainHGDir} --subrepo-map=${workspaceDir}/submodule-mappings
    elif ${tags}; then
        ${fastExportDir}/hg-fast-export.sh -r ${mainHGDir} -T ${workspaceDir}/tags.map --hgtags
    else
        ${fastExportDir}/hg-fast-export.sh -r ${mainHGDir}
    fi
    if [ $? -ne 0 ]
    	then
    		echo -e "The Fast Export command did not run properly!"
    		exit 1
    	fi
    if ${subs}; then
        rm ${workspaceDir}/submodule-mappings
    fi
    git checkout HEAD
    #convert the .hgignore to .gitignore
    if [[ -f .hgignore ]]; then
        mv .hgignore .gitignore
        sed -i '/# use glob syntax./d' ./.gitignore
        sed -i '/syntax: glob/d' ./.gitignore
    fi
    #remove all the .hg files
    rm -rf .hg*
    #Add the local stuff to remote
    git add .
    git commit -m "Converted HG to Git"
    #Create the main repo in BitBucket
    curl -s -X POST -H "${AUTH}" -H "Content-Type: application/json" -d '{
        "scm": "git",
        "project": {
            "key": "'${projectKeyName}'"
        },
        "fork_policy": "no_public_forks",
        "is_private": "true"
    }' ${APIURL}/${mainGitRepoName}
    
    git remote add origin ${GitURL}/${mainGitRepoName}.git
    git push -u origin master
    if ${tags}; then
        git push --all
        git push --tags
    else
        git push --all
    fi
}

cd ${mainHGDir}
if ${subs}; then
    echo "There are sub repos found. Do you want to run the script? yes/no: "
    read answer 
    if [[ answer == "no" ]]; then
        echo "Exiting..."
        exit 0
    else
        echo "Continuing..."
        doSubRepos
    fi
else
    echo "No submodules. Doing main repo..."
fi
mainRepo
