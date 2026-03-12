// NovaConnector.cpp - Implementation
#include "NovaConnector.h"
#include "HttpModule.h"
#include "JsonObjectConverter.h"

ANovaConnector::ANovaConnector()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ANovaConnector::BeginPlay()
{
    Super::BeginPlay();
}

void ANovaConnector::StartHeartbeat()
{
    if (HeartbeatInterval > 0)
    {
        GetWorld()->GetTimerManager().SetTimer(
            HeartbeatTimer, 
            this, 
            &ANovaConnector::SendWorldState, 
            HeartbeatInterval, 
            true
        );
    }
}

void ANovaConnector::SendWorldState()
{
    // This would gather world data and send to Nova
    // For now, just request a decision
    RequestNovaDecision();
}

void ANovaConnector::RequestNovaDecision()
{
    // Create HTTP request
    TSharedRef<IHttpRequest> Request = FHttpModule::Get().CreateRequest();
    
    FString URL = NovaAPIBaseURL + "/nova/think";
    Request->SetURL(URL);
    Request->SetVerb("POST");
    Request->SetHeader("Content-Type", "application/json");
    
    // Build minimal world state
    FString JsonBody = "{\"agents\":[],\"resources\":[],\"structures\":[],\"players\":[]}";
    Request->SetContentAsString(JsonBody);
    
    Request->OnProcessRequestComplete().BindLambda([this](FHttpRequestPtr Request, FHttpResponsePtr Response, bool bConnectedSuccessfully)
    {
        if (bConnectedSuccessfully && Response->GetResponseCode() == 200)
        {
            FString ResponseStr = Response->GetContentAsString();
            OnResponseReceived(ResponseStr);
        }
    });
    
    Request->ProcessRequest();
}

void ANovaConnector::OnResponseReceived(FString Response)
{
    // Parse the JSON response and trigger Blueprint events
    // This would convert JSON to Blueprint-usable data
    UE_LOG(LogTemp, Warning, TEXT("Nova Response: %s"), *Response);
}

void ANovaConnector::ExecuteNovaOrders(FString OrdersJson)
{
    // Parse orders and trigger individual order events
    OnNovaOrderReceived("default", "explore", FVector::ZeroVector);
}
