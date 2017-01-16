/*
 *   see CC150 OO Design for details.
 *   1) n levels, each level has m rows of spots and each row has k spots.So each level has m x k spots.
 *   2) The parking lot can park motorcycles, cars and buses
 *   3) The parking lot has motorcycle spots, compact spots, and large spots
 *   4) Each row, motorcycle spots id is in range [0,k/4)(0 is included, k/4 is not included), compact spots id is in range [k/4,k/4*3) and large spots id is in range [k/4*3,k).
 *   5) A motorcycle can park in any spot
 *   6) A car park in single compact spot or large spot
 *   7) A bus can park in five large spots that are consecutive and within same row. it can not park in small spots
 *
 *   Example
 *   level=1, num_rows=1, spots_per_row=11
 *   parkVehicle("Motorcycle_1") // return true
 *   parkVehicle("Car_1") // return true
 *   parkVehicle("Car_2") // return true
 *   parkVehicle("Car_3") // return true
 *   parkVehicle("Car_4") // return true
 *   parkVehicle("Car_5") // return true
 *   parkVehicle("Bus_1") // return false
 *   unParkVehicle("Car_5")
 *   parkVehicle("Bus_1") // return true
 *
 */

enum class VehicleSize { Motorcycle, Compact, Large };

class Vehicle;
class Level;

class ParkingSpot {
public:
    ParkingSpot(Level *lvl, int r, int n, VehicleSize s): _level(lvl), _row(r), _spotNumber(n), _spotSize(s) {} // ...
    bool isAvailable() { return _vehicle == nullptr; };
    bool canFitVehicle(Vehicle *vehicle) {} // ...
    bool park(Vehicle *v) {} // ...
    int getRow() { return _row; }
    int getSpotNumber() { return _spotNumber; }
    void removeVehicle() {} // ... 

private:
    Vehicle *_vehicle = nullptr;
    VehicleSize _spotSize;
    int _row;
    int _spotNumber;
    Level *_level = nullptr;
};

class Vehicle {
public:
    Vehicle() {}
    int getSpotsNeeded() { return _spotsNeeded; }
    VehicleSize getSize() { return _size; }
    void parkInSpot(ParkingSpot s) { _parkingSpots.push_back(s); }
    void clearSpots() {} // ...
    virtual bool canFitInSpot(ParkingSpot spot) {}

protected:
    vector<ParkingSpot> _parkingSpots;
    string _licensePlate;
    int _spotsNeeded;
    VehicleSize _size;
};

class Bus: public Vehicle {
public:
    Bus() {
        _spotsNeeded = 5;
        _size = VehicleSize::Large;
    }
    bool canFitInSpot(ParkingSpot spot) { }
};

class Car: public Vehicle {
public:
    Car() {
        _spotsNeeded = 1;
        _size = VehicleSize::Compact;
    }
    bool canFitInSpot(ParkingSpot spot) { }
};

class Motorcycle: public Vehicle {
public:
    Motorcycle() {
        _spotsNeeded = 1;
        _size = VehicleSize::Motorcycle;
    }
    bool canFitInSpot(ParkingSpot spot) { }
};

class Level {
public:
    Level() {}
    Level(int flr, int numberSpots): _floor(flr), _availableSpots(numberSpots) {}
    Level(const Level* lvl) {
        *this = *lvl;
    }
    int availableSpots() { return _availableSpots; }
    bool parkVehicle(Vehicle vehicle) {} // ...
    void spotFreed() { ++_availableSpots; }

private:
    int _floor;
    vector<ParkingSpot> _spots;
    int _availableSpots = 0;
    static const int _SPOTS_PER_ROW = 10;
    bool parkStartingAtSpot(int num, Vehicle v) {} // ...
    int findAvailableSpots(Vehicle vehicle) {} // ...
};

class ParkingLot {
public:
    ParkingLot() {} // ...
    bool parkVehicle(Vehicle vehicle) {} // ...

private:
    vector<Level> _levels;
    const int _NUM_LEVELS = 5;
};