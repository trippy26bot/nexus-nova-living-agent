// NovaConnector.h - Unreal API Connector
// This actor connects Novas World to the Nova AI Brain

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NovaConnector.generated.h"

UCLASS()
class NOVASWORLD_API ANovaConnector : public AActor
{
    GENERATED_BODY()
    
public:    
    ANovaConnector();

protected:
    virtual void BeginPlay() override;

public:    
    // Timer handle for heartbeat
    FTimerHandle HeartbeatTimer;

    // Configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Nova")
    FString NovaAPIBaseURL = "http://localhost:8000";

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Nova")
    float HeartbeatInterval = 2.0f;

    // Send world state to Nova
    UFUNCTION(BlueprintCallable, Category = "Nova")
    void SendWorldState();

    // Get Nova's response
    UFUNCTION(BlueprintCallable, Category = "Nova")
    void RequestNovaDecision();

    // Parse and execute Nova's orders
    UFUNCTION(BlueprintCallable, Category = "Nova")
    void ExecuteNovaOrders(FString OrdersJson);

    // Blueprint implementable events
    UFUNCTION(BlueprintImplementableEvent, Category = "Nova")
    void OnNovaOrderReceived(FString AgentID, FString Goal, FVector TargetLocation);

    // Start the heartbeat loop
    UFUNCTION(BlueprintCallable, Category = "Nova")
    void StartHeartbeat();

private:
    // Internal HTTP callback
    void OnResponseReceived(FString Response);
};
