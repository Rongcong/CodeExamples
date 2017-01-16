/*
 * PerceptronTrainer.cpp
 *
 *  Created on: Dec 9, 2016
 *      Author: Rongcong
 */
#include <iostream>
#include <stdlib.h>

using namespace std;

class Vector {
public:
	Vector(float x0, float x1, float x2, float x3) : _x0(x0), _x1(x1), _x2(x2), _x3(x3) {}
	Vector(float x1, float x2, float x3) : _x0(1), _x1(x1), _x2(x2), _x3(x3) {}
	float operator*(const Vector& rhs) {
		float sumProduct = (float) (this->_x0*rhs._x0 + this->_x1*rhs._x1 + this->_x2*rhs._x2 + this->_x3*rhs._x3);
		return sumProduct;
	}

	Vector operator*(float a) {
		Vector result;
		result._x0 = a * _x0;
		result._x1 = a * _x1;
		result._x2 = a * _x2;
		result._x3 = a * _x3;
		return result;		
	}

	Vector operator+(const Vector& rhs) {
		Vector result;
		result._x0 = rhs._x0 + _x0;
		result._x1 = rhs._x1 + _x1;
		result._x2 = rhs._x2 + _x2;
		result._x3 = rhs._x3 + _x3;
		return result;
	}

	void operator()(const Vector& rhs) {
		_x0 = rhs._x0;
		_x1 = rhs._x1;
		_x2 = rhs._x2;
		_x3 = rhs._x3;
	}
	
private:
	float _x0, _x1, _x2, _x3;
};

class Perceptron {
public:
	Perceptron(Vector T, Vector W): target(T), weight(W) {
		srand(time(NULL));
	}

	void print() {
		cout << weight._x0 << " " << weight._x1 << " " << weight._x2 << " " << weight._x3 << endl;
	}

	void train(int num) {
		assert(num > 0);
		for (int i = 0; i < num; i++) {
			calculate();
			update();
		}
	}
	
private:
	Vector input;
	Vector weight;
	Vector target;
	int output;
	int y;

	void update() {
		weight += 0.1*(y-output)*input;
	}

	void calculate() {
		input._x0 = (rand()/(float)) RAND_MAX * 20 - 10;
		input._x1 = (rand()/(float)) RAND_MAX * 20 - 10;
		input._x2 = (rand()/(float)) RAND_MAX * 20 - 10;
		input._x3 = (rand()/(float)) RAND_MAX * 20 - 10;
		y = input * target > 0 ? 1 : 0; 
		output = input * weight > 0 ? 1 : 0;
	}
};


int main() {
	Vector target(2, 1, -1, -1);
	Vector weight(0.4, -0.2, 0.1, -0.5);
	Perceptron p(target, weight);
	p.train(10000);
	p.print();
	return 0;
}