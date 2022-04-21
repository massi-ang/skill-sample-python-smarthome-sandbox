import { CfnRoute, HttpApi, HttpAuthorizer, HttpAuthorizerType, HttpMethod } from '@aws-cdk/aws-apigatewayv2';
import { LambdaProxyIntegration } from '@aws-cdk/aws-apigatewayv2-integrations';
import { AttributeType, ProjectionType, Table } from '@aws-cdk/aws-dynamodb';
import { Effect, PolicyStatement } from '@aws-cdk/aws-iam';
import { Code, Function, Runtime } from '@aws-cdk/aws-lambda';
import * as cdk from '@aws-cdk/core';
import { CfnOutput, DefaultTokenResolver, Duration, Size } from '@aws-cdk/core';
// import * as sqs from '@aws-cdk/aws-sqs';

export class AlexaBackendStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    /**
     * Endpoint API
     */

    const endpointRestApi = new HttpApi(this, 'endpointRestApi', {
      apiName: "EndpointCloud",
      description: "An Endpoint cloud API",
    });

    /**
     * Endpoint Details table
     */

    const endpointsDetailsTable = new Table(this, 'EndpointsDetailsTable', {
      partitionKey: {
        name: "EndpointId",
        type: AttributeType.STRING,
      },
      readCapacity: 5,
      writeCapacity: 5,
    });

    endpointsDetailsTable.addGlobalSecondaryIndex({
      partitionKey: {
        name: "UserId",
        type: AttributeType.STRING
      },
      indexName: "byUserId",
      projectionType: ProjectionType.ALL
    })


    /**
     * Users table
     */

    const usersTable = new Table(this, 'UsersTable', {
      partitionKey: {
        name: "UserId",
        type: AttributeType.STRING,
      },
      readCapacity: 5,
      writeCapacity: 5,
    })

    /**
     * Endpoint Lambda
     * 
     */

    const endpointLambda = new Function(this, 'EndpointAdapter', {
      code: Code.fromAsset("../lambda/api"),
      runtime: Runtime.PYTHON_3_9,
      memorySize: Size.mebibytes(128).toMebibytes(),
      handler: 'index.handler',
      environment: {
        "api_id": endpointRestApi.apiId,
        "ENDPOINT_DETAILS_TABLE": endpointsDetailsTable.tableName,
        "USERS_TABLE": usersTable.tableName
      },
      timeout: Duration.seconds(6)
    });

    endpointLambda.addToRolePolicy(new PolicyStatement({
      actions: ["execute-api:Invoke"],
      resources: [ "arn:aws:execute-api:*:*:*" ],
      effect: Effect.ALLOW
    }));

    endpointLambda.addToRolePolicy(new PolicyStatement({
      actions: ["logs:*"],
      resources: [ "arn:aws:logs:*:*:*" ],
      effect: Effect.ALLOW
    }));


    endpointLambda.addToRolePolicy(new PolicyStatement({
      actions: ["iot:AddThingToThingGroup",
                "iot:CreateThing",
                "iot:CreateThingType",
                "iot:CreateThingGroup",
                "iot:DescribeThing",
                "iot:GetThingShadow",
                "iot:ListThings",
                "iot:ListThingGroups",
                "iot:UpdateThing",
                "iot:UpdateThingShadow"
              ],
      resources: [ "*" ],
      effect: Effect.ALLOW
    }))

    endpointsDetailsTable.grantFullAccess(endpointLambda);
    usersTable.grantFullAccess(endpointLambda);
    /**
     * Skills Adapter Lambda
     * 
     * This lambda function is the one being called by Alexa for the integration
     * with your smart home skill. It simply acts as a pass-through to invoke the backend
     * API.
     */

    const skillLambda = new Function(this, 'SkillAdapter', {
      code: Code.fromAsset("../lambda/smarthome"),
      runtime: Runtime.PYTHON_3_9,
      memorySize: Size.mebibytes(128).toMebibytes(),
      handler: 'index.handler',
      environment: {
        "api_id": endpointRestApi.apiId,
      },
      timeout: Duration.seconds(7)
    })

    skillLambda.addToRolePolicy(new PolicyStatement({
      actions: ["execute-api:Invoke"],
      resources: [ "arn:aws:execute-api:*:*:*" ],
      effect: Effect.ALLOW
    }));

    /**
     * List of all routes added to the API
     */

    let routes = endpointRestApi.addRoutes({
      path: "/endpoints",
      integration: new LambdaProxyIntegration({
        handler: endpointLambda,
      }),
      methods: [HttpMethod.GET, HttpMethod.POST, HttpMethod.DELETE]
      });

    routes = routes.concat(endpointRestApi.addRoutes({
      path: "/directives",
      integration: new LambdaProxyIntegration({
        handler: endpointLambda,
      }),
      methods: [HttpMethod.POST]
    }));

    routes = routes.concat(endpointRestApi.addRoutes({
      path: "/events",
      integration: new LambdaProxyIntegration({
        handler: endpointLambda,
      }),
      methods: [HttpMethod.POST]
    }));

    /**
     * Sets AWS_IAM as authorizer on all routes as this is not yet supported
     * in the high level constructs
     */

    // routes.forEach(r => {
    //   const routeCfn = r.node.defaultChild as CfnRoute;
    //   routeCfn.authorizationType = "AWS_IAM";
    // });
    
    new CfnOutput(this, 'EndpointAPIID', {
      value: endpointRestApi.apiId,
      description: "The Endpoint API ID",
      exportName: "endpoint-api-id"
    });

    new CfnOutput(this, 'EndpointAPIURL', {
      value: `https:/${endpointRestApi.apiId}.execute-api.${this.region}.amazonaws.com/`,
      description: 'Endpoint API URL',
      exportName: 'endpoint-api-url'
    });

    new CfnOutput(this, 'EndpointAPIAuthRediurectURL', {
      value: `https:/${endpointRestApi.apiId}.execute-api.${this.region}.amazonaws.com/auth-redirect`, 
      description: 'The Endpoint API Auth-Redirect URL',
      exportName: 'endpoint-api-auth-redirect-url'
    });

    new CfnOutput(this, 'SkillAdapterLambdaArn', {
      value: skillLambda.functionArn,
      description: 'Skill Adapter Lambda ARN'
    });

    new CfnOutput(this, 'EndpointDetailsTableOutput', {
      value: endpointsDetailsTable.tableName,
      description: 'Endpoint Details Table Name'
    });

    new CfnOutput(this, 'UsersTableOutput', {
      value: usersTable.tableName,
      description: 'Users Table Name'
    });
  }
}
