#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include "structmember.h"
#include "math.h"

static const double RS_EPS = 1e-7;
static const double SAT_MAX = 1e5;
static const size_t SAT_ITERATIONS = 100;

static double normalize(const double a) {
    double L = a / (log(fabs(a) + 1.0) + RS_EPS);
    double N = log(fabs(L) + RS_EPS) / (log(fabs(L) + 1.0) + RS_EPS);
    return copysign(L * N, a);
}

static double geom_mean(const double a, const double b) {
    return sqrt(a * b);
}

typedef struct {
    PyObject_HEAD
    double attacker;
    double victim;
    double game_hardness;
    unsigned char inflation;
} RatingSystem;

static double get_probability(const RatingSystem *rs, const double a, const double b) {
    return 1.0 / (1.0 + pow(10.0, (b - a) / rs->game_hardness));
}

static double get_seed(const RatingSystem *rs, const double rating, const double player_rating) {
    double ret = 1.0;

    ret += get_probability(rs, rs->attacker, rating);
    ret += get_probability(rs, rs->victim, rating);

    ret -= get_probability(rs, rating, player_rating);

    return ret;
}

static double get_satisfaction(const RatingSystem *rs, const double need_place, const double player_rating) {
    double l = 0;
    double r = SAT_MAX;
    for (size_t i = 0; i < SAT_ITERATIONS; ++i) {
        double mid = (l + r) / 2.0;
        double seed = get_seed(rs, mid, player_rating);
        if (seed < need_place) {
            r = mid;
        } else {
            l = mid;
        }
    }

    return l;
}

static double calculate_delta(const RatingSystem *rs, const double rating, const double place) {
    double seed = get_seed(rs, rating, rating);
    double mean = geom_mean(seed, place);
    double R = get_satisfaction(rs, mean, rating);

    return (R - rating) / 2.0;
}

static PyModuleDef rating_system = {
    PyModuleDef_HEAD_INIT,
    .m_name = "custom",
    .m_doc = "Rating system module",
    .m_size = -1,
};

static int
RatingSystem_init(RatingSystem *self, PyObject *args, PyObject *kwargs) {
    static char *kwargs_list[] = {"attacker", "victim", "game_hardness", "inflation", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|$dddb", kwargs_list,
                                      &self->attacker, &self->victim,
                                      &self->game_hardness, &self->inflation)) {
        return -1;
    }

    if (self->game_hardness < RS_EPS) {
        self->game_hardness = 1300.0;
    }

    if (self->inflation > 0) {
        self->inflation = 1;
    }

    return 0;
}

static PyMemberDef RatingSystem_members[] = {
    {"attacker", T_DOUBLE, offsetof(RatingSystem, attacker), 0, "attacker score"},
    {"victim", T_DOUBLE, offsetof(RatingSystem, victim), 0, "victim name"},
    {"game_hardness", T_DOUBLE, offsetof(RatingSystem, game_hardness), 0, "game hardness"},
    {"inflation", T_UBYTE, offsetof(RatingSystem, inflation), 0, "inflation"},
    {NULL}  /* Sentinel */
};

static PyObject *
RatingSystem_calculate(RatingSystem *self) {
    double attacker_delta = calculate_delta(self, self->attacker, 1);
    double victim_delta = calculate_delta(self, self->victim, 2);

    if (self->inflation) {
        double sum_deltas = attacker_delta + victim_delta;
        double dec = sum_deltas / 2.0;

        attacker_delta -= dec;
        victim_delta -= dec;

        attacker_delta = normalize(attacker_delta);
        victim_delta = normalize(victim_delta);

        victim_delta = fmax(victim_delta, -self->victim);
    } else {
        double norm = fmin(fabs(attacker_delta), fabs(victim_delta));
        attacker_delta = copysign(norm, attacker_delta);
        victim_delta = copysign(norm, victim_delta);

        double suggested_attacker_delta = normalize(attacker_delta);
        double suggested_victim_delta = normalize(victim_delta);

        attacker_delta = fmin(attacker_delta, suggested_attacker_delta);
        victim_delta = fmax(victim_delta, suggested_victim_delta);
    }

    PyObject *result = Py_BuildValue("dd", attacker_delta, victim_delta);

    return result;
}


static PyMethodDef RatingSystem_methods[] = {
    {"calculate", (PyCFunction) RatingSystem_calculate, METH_NOARGS, "Calculate attacker & victim deltas"},
    {NULL}  /* Sentinel */
};

static PyTypeObject RatingSystemType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "rating_system.RatingSystem",
    .tp_doc = "RatingSystem object",
    .tp_basicsize = sizeof(RatingSystem),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc) RatingSystem_init,
    .tp_members = RatingSystem_members,
    .tp_methods = RatingSystem_methods,
};

PyMODINIT_FUNC
PyInit_rating_system(void)
{
    PyObject *m;
    if (PyType_Ready(&RatingSystemType) < 0)
        return NULL;

    m = PyModule_Create(&rating_system);
    if (m == NULL)
        return NULL;

    Py_INCREF(&RatingSystemType);
    PyModule_AddObject(m, "RatingSystem", (PyObject *) &RatingSystemType);
    return m;
}
