version: 0.2

phases:
  build:
    commands:
      - PATH="$PATH:$CODEBUILD_SRC_DIR/fraud-detection-and-prevention-fdp-agentic-platform/bin" && export PATH
      - if [ -d "$CODEBUILD_SRC_DIR/fraud-detection-and-prevention-fdp-agentic-platform" ]; then mv $CODEBUILD_SRC_DIR/fraud-detection-and-prevention-fdp-agentic-platform/ temp/; fi
      - git clone https://github.com/aws-samples/fraud-detection-and-prevention-fdp-agentic-platform
      - if [ -d "temp" ]; then cp -R temp/ $CODEBUILD_SRC_DIR/fraud-detection-and-prevention-fdp-agentic-platform/; rm -rf temp; fi
      - cd $CODEBUILD_SRC_DIR/fraud-detection-and-prevention-fdp-agentic-platform/
      - if [ -n "$FDP_GITHUB_BRANCH" ]; then git checkout $FDP_GITHUB_BRANCH; fi
      - AWS_ASSUME_ROLE=$(aws sts assume-role --role-arn ${role_arn} --role-session-name fdp-`date '+%Y-%m-%d-%H-%M-%S'`) && export AWS_ASSUME_ROLE
      - AWS_ACCESS_KEY_ID=$(echo "$AWS_ASSUME_ROLE" | jq -r '.Credentials.AccessKeyId') && export AWS_ACCESS_KEY_ID
      - AWS_SECRET_ACCESS_KEY=$(echo "$AWS_ASSUME_ROLE" | jq -r '.Credentials.SecretAccessKey') && export AWS_SECRET_ACCESS_KEY
      - AWS_SESSION_TOKEN=$(echo "$AWS_ASSUME_ROLE" | jq -r '.Credentials.SessionToken') && export AWS_SESSION_TOKEN
      - mkdir -p $HOME/.aws/ && touch $HOME/.aws/config && touch $HOME/.aws/credentials
      - echo "[default]" >> $HOME/.aws/config
      - echo "region=$AWS_DEFAULT_REGION" >> $HOME/.aws/config
      - echo "[default]" >> $HOME/.aws/credentials
      - echo "aws_access_key_id=$AWS_ACCESS_KEY_ID" >> $HOME/.aws/credentials
      - echo "aws_secret_access_key=$AWS_SECRET_ACCESS_KEY" >> $HOME/.aws/credentials
      - echo "aws_session_token=$AWS_SESSION_TOKEN" >> $HOME/.aws/credentials
      - /bin/bash ./bin/deploy.sh -d $FDP_DIR -r $FDP_REGION -s $FDP_BUCKET -i $FDP_GID

cache:
  paths:
    - $CODEBUILD_SRC_DIR/fraud-detection-and-prevention-fdp-agentic-platform
