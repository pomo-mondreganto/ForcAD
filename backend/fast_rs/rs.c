#include "postgres.h"
#include "fmgr.h"
#include "funcapi.h"
#include "access/heapam.h"
#include "catalog/pg_type.h"

#include "math.h"

#ifdef PG_MODULE_MAGIC
PG_MODULE_MAGIC;
#endif

static const double RS_EPS = 1e-7;
static const double SAT_MAX = 1e5;
static const size_t SAT_ITERATIONS = 100;

static double
normalize(const double a)
{
    double L = a / (log(fabs(a) + 1.0) + RS_EPS);
    double N = log(fabs(L) + RS_EPS) / (log(fabs(L) + 1.0) + RS_EPS);
    return copysign(L * N, a);
}

static double
geom_mean(const double a, const double b)
{
    return sqrt(a * b);
}

typedef struct
{
    double attacker;
    double victim;
    double game_hardness;
    bool inflation;
} RatingSystem;

static double
get_probability(const RatingSystem *rs, const double a, const double b)
{
    return 1.0 / (1.0 + pow(10.0, (b - a) / rs->game_hardness));
}

static double
get_seed(const RatingSystem *rs, const double rating, const double player_rating)
{
    double ret = 1.0;

    ret += get_probability(rs, rs->attacker, rating);
    ret += get_probability(rs, rs->victim, rating);
    ret -= get_probability(rs, rating, player_rating);

    return ret;
}

static double
get_satisfaction(const RatingSystem *rs, const double need_place, const double player_rating)
{
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

static double
calculate_delta(const RatingSystem *rs, const double rating, const double place)
{
    double seed = get_seed(rs, rating, rating);
    double mean = geom_mean(seed, place);
    double R = get_satisfaction(rs, mean, rating);

    return (R - rating) / 2.0;
}

PG_FUNCTION_INFO_V1(calculate);

Datum
calculate(PG_FUNCTION_ARGS)
{
    RatingSystem *self = palloc0(sizeof(RatingSystem));
    self->attacker = PG_GETARG_FLOAT8(0);
    self->victim = PG_GETARG_FLOAT8(1);
    self->game_hardness = PG_GETARG_FLOAT8(2);
    self->inflation = PG_GETARG_BOOL(3);

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

    // below is the code to return tuple of (attacker_delta, victim_delta) to PostgreSQL
    TupleDesc resultTupleDesc;
    Datum retvals[2];
    bool retnulls[2];
    HeapTuple rettuple;

    resultTupleDesc = CreateTemplateTupleDesc(2);
    TupleDescInitEntry(resultTupleDesc, (AttrNumber) 1, "attacker_delta", FLOAT8OID, -1, 0);
    TupleDescInitEntry(resultTupleDesc, (AttrNumber) 2, "victim_delta", FLOAT8OID, -1, 0);

    if (get_call_result_type(fcinfo, NULL, &resultTupleDesc) != TYPEFUNC_COMPOSITE) {
        ereport(ERROR, (errcode(ERRCODE_FEATURE_NOT_SUPPORTED),
                    errmsg("function returning record called in context that cannot accept type record")));
    }
    resultTupleDesc = BlessTupleDesc(resultTupleDesc);
    retvals[0] = Float8GetDatum(attacker_delta);
    retvals[1] = Float8GetDatum(victim_delta);
    retnulls[0] = 0;
    retnulls[1] = 0;
    rettuple = heap_form_tuple(resultTupleDesc, retvals, retnulls);
    PG_RETURN_DATUM(HeapTupleGetDatum(rettuple));
}
