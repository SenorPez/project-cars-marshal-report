<?php

$data = json_decode(file_get_contents('output.json'));
print(live_timing());

function live_timing() {
    global $data;
    $return_value = "";
    $return_value .= "<table>";

    foreach (drivers_by_position($data->drivers) as $driver) {
        $return_value .= "<tr>";
        $return_value .= "<td>{$driver->driver}</td>";
        $return_value .= "<td>".format_time($driver->best_lap_time)."</td>";
        #TODO: Gap time.
        $return_value .= "<td>".get_last_sector_time($driver, 1)."</td>";
        $return_value .= "<td>".get_last_sector_time($driver, 2)."</td>";
        $return_value .= "<td>".get_last_sector_time($driver, 3)."</td>";
        $return_value .= "<td>".get_lap_number($driver)."</td>";
        $return_value .= "</tr>";
    }
    $return_value .= "</table>";

    return $return_value;
}

function get_lap_number($driver) {
    $lap = end($driver->laps);

    if ($lap->lap_time) {
        return $lap->lap_number;
    } else {
        return ($lap->lap_number-1 > 0) ? $lap->lap_number-1 : "";
    }
}

function get_last_sector_time($driver, $sector) {
    $lap = end($driver->laps);
    $sector = "sector_".$sector;

    if ($lap->$sector) {
        return format_time($lap->$sector);
    } else {
        $lap = prev($driver->laps);
        
        if ($lap->$sector) {
            return format_time($lap->$sector);
        } else {
            return "";
        }
    }
}

function format_time($time) {
    $minutes = floor(($time / 60) % 60);
    $seconds = $time % 60;

    return "$minutes:$seconds";
}

function drivers_by_position($drivers) {
    $sorted_drivers = $drivers;
    if (uasort($sorted_drivers, "compare_position")) {
        return $sorted_drivers;
    }
}

function compare_position($a, $b) {
    $lap_a = end($a->laps);

    if ($lap_a->position == NULL) {
        $lap_a = prev($a->laps);
    }

    $lap_b = end($b->laps);

    if ($lap_b->position == NULL) {
        $lap_b = prev($b->laps);
    }

    return ($lap_a->position < $lap_b->position) ? -1 : 1;
}

?>
