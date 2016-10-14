class NumMatrix {
    int _numRow = 0;
    int _numCol = 0;
    vector<vector<int>> _matrix;
    vector<vector<int>> _bit;
    
    void add(int row, int col, int val) {
        ++row;
        ++col;
        while(row <= _numRow) {
            int colIdx = col;
            while(colIdx <= _numCol) {
                _bit[row][colIdx] += val;
                colIdx += (colIdx & (-colIdx));
            }
            row += (row & (-row));
        }
    }
    
    int region(int row, int col) {
        ++row;
        ++col;
        int res = 0;
        while(row > 0) {
            int colIdx = col;
            while(colIdx > 0) {
                res += _bit[row][colIdx];
                colIdx -= (colIdx & (-colIdx));
            }
            row -= (row & (-row));
        }
        return res;
    }
    
public:
    NumMatrix(vector<vector<int>> &matrix) {
        if (!matrix.size() || !matrix[0].size()) return;
        _numRow = matrix.size();
        _numCol = matrix[0].size();
        _matrix = matrix;
        _bit = vector<vector<int>> (_numRow+1, vector<int>(_numCol+1, 0));
        for (int i = 0; i < _numRow; ++i)
            for (int j = 0; j < _numCol; ++j)
                add(i, j, matrix[i][j]);
    }

    void update(int row, int col, int val) {
        int diff = val - _matrix[row][col];
        if (diff) {
            add(row, col,diff);
            _matrix[row][col] = val;
        }
    }

    int sumRegion(int row1, int col1, int row2, int col2) {
        return region(row2, col2) - region(row2, col1-1) - region(row1-1, col2) + region(row1-1, col1-1);
    }
};