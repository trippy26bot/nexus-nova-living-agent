# Nova Connector - Super Simple Blueprint Only

## Step 1: Create the Actor
1. Right-click in Content Browser → Blueprint Class → Actor
2. Name: `BP_NovaConnector`
3. Open it

## Step 2: Add Variables
In the Blueprint, click "+" on Variables:
- `APIURL` (String) = "http://localhost:8000"
- `HeartbeatInterval` (Float) = 2.0

## Step 3: Event Graph - Add These Nodes
Connect them like this:

```
Event BeginPlay
    |
    +--> Set Timer by Event (2.0 sec, Looping)
             |
             +--> Custom Event "OnTick" (make this)
                       |
                       +--> Make HTTP Request
                               |
                               +--> (Connect to On Success)
                                       |
                                       +--> Print String (to see response)
```

## Step 4: The HTTP Request Node
- **URL**: `http://localhost:8000/nova/think`
- **Verb**: POST
- **Content-Type**: application/json
- **Body**: `{"agents":[],"resources":[],"structures":[],"players":[]}`

## Step 5: Add to Level
1. Drag `BP_NovaConnector` into your level
2. Press Play

## That's It!
You should see HTTP responses printing in the output log.

---

## Even Simpler Test FIRST
Before connecting to Nova, test HTTP works:

1. Create Blueprint Actor
2. Event BeginPlay → Make HTTP Request to `http://httpbin.org/post`
3. On Success → Print String

If that works, then connect to Nova.
